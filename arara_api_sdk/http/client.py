import logging
from typing import Any, Callable, Dict, Mapping, Optional, Tuple, Type, TypeVar, Union

import httpx
from pydantic import BaseModel
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    Retrying,
    stop_after_attempt,
    wait_exponential,
)

from arara_api_sdk._version import __version__
from arara_api_sdk.config import SDKConfig
from arara_api_sdk.exceptions import (
    AraraApiError,
    AraraAuthError,
    AraraConnectionError,
    AraraError,
    AraraForbiddenError,
    AraraPlanFeatureLockedError,
    AraraRateLimitError,
    AraraResourceNotFoundError,
    AraraServerError,
    AraraTimeoutError,
    AraraUnprocessableError,
    AraraValidationError,
)

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger("arara_sdk")

RETRYABLE_EXCEPTIONS = (
    httpx.ConnectError,
    httpx.TimeoutException,
    AraraServerError,
    AraraRateLimitError,
)

MAX_RETRY_AFTER_SECONDS = 60
IDEMPOTENCY_HEADER = "Idempotency-Key"
PLAN_FEATURE_LOCKED = "PLAN_FEATURE_LOCKED"
RETRY_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})

_STATUS_ERRORS: Dict[int, Type[AraraError]] = {
    400: AraraValidationError,
    401: AraraAuthError,
    404: AraraResourceNotFoundError,
    422: AraraUnprocessableError,
    429: AraraRateLimitError,
}
UNKNOWN_ERROR_MESSAGE = "Unknown error"

_EXPONENTIAL_BACKOFF = wait_exponential(multiplier=1, min=2, max=10)


def _exception_from(retry_state: RetryCallState) -> Optional[BaseException]:
    """Return the exception raised by the last attempt, if it failed."""
    outcome = retry_state.outcome
    if outcome is None or not outcome.failed:
        return None
    return outcome.exception()


def _should_retry(retry_state: RetryCallState) -> bool:
    """Retry transport errors, 5xx and 429.

    A 429 whose Retry-After exceeds the cap is not worth sleeping on: retrying
    earlier than the server asked just burns an attempt, and blocking the caller
    for that long is worse than surfacing the error.
    """
    exception = _exception_from(retry_state)
    if isinstance(exception, AraraRateLimitError):
        return (
            exception.retry_after is None
            or exception.retry_after <= MAX_RETRY_AFTER_SECONDS
        )
    return isinstance(exception, RETRYABLE_EXCEPTIONS)


def _never_retry(retry_state: RetryCallState) -> bool:
    """Retry policy for non-idempotent calls: a second attempt could duplicate."""
    return False


def _retry_policy(
    method: str, headers: Optional[Mapping[str, str]]
) -> Callable[[RetryCallState], bool]:
    """Pick the retry policy for a call.

    GET and other idempotent methods retry freely. A POST/PATCH only retries
    when it carries an ``Idempotency-Key``: the same key travels on every
    attempt, so the API collapses duplicates instead of sending twice.
    """
    if method.upper() in RETRY_SAFE_METHODS:
        return _should_retry
    key = headers.get(IDEMPOTENCY_HEADER) if headers else None
    if isinstance(key, str) and key.strip():
        return _should_retry
    return _never_retry


def _error_class(status_code: int, code: Optional[str]) -> Type[AraraError]:
    """Map status and envelope code to the exception type."""
    if status_code == 403:
        if code is None:
            return AraraForbiddenError
        if code == PLAN_FEATURE_LOCKED:
            return AraraPlanFeatureLockedError
        return AraraApiError
    if 500 <= status_code < 600:
        return AraraServerError
    return _STATUS_ERRORS.get(status_code, AraraError)


def _wait_strategy(retry_state: RetryCallState) -> float:
    """Honor Retry-After on 429, fall back to exponential backoff."""
    exception = _exception_from(retry_state)
    if isinstance(exception, AraraRateLimitError) and exception.retry_after is not None:
        return float(exception.retry_after)
    return _EXPONENTIAL_BACKOFF(retry_state)


class HttpClient:
    """Internal HTTP client for Arara API with sync and async support."""

    def __init__(self, config: SDKConfig):
        """Build the sync and async httpx clients and the shared retry policy."""
        self.config = config
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "User-Agent": f"Arara-Python-SDK/{__version__}",
        }
        self._retry_config: Dict[str, Any] = {
            "retry": _should_retry,
            "wait": _wait_strategy,
            "stop": stop_after_attempt(self.config.max_retries + 1),
            "reraise": True,
        }
        self.sync_client = httpx.Client(
            base_url=self.config.base_url,
            headers=self._headers,
            timeout=self.config.timeout,
        )
        self.async_client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers=self._headers,
            timeout=self.config.timeout,
        )

    @staticmethod
    def _parse_retry_after(response: httpx.Response) -> Optional[int]:
        """Parse the Retry-After header as seconds, if present and numeric."""
        header = response.headers.get("Retry-After")
        if header is None:
            return None
        try:
            return max(int(header.strip()), 0)
        except ValueError:
            return None

    @staticmethod
    def _parse_error_envelope(
        error_data: Any,
    ) -> Tuple[Optional[str], str, Dict[str, Any]]:
        """Extract code, message and details from an API error body.

        The Arara envelope is ``{"error": {"code", "message", "details"}}``.
        Bodies where ``error``/``message`` carry a bare string are still
        accepted, so older deployments and non-JSON responses keep working.
        """
        if not isinstance(error_data, dict):
            return None, str(error_data) or UNKNOWN_ERROR_MESSAGE, {}

        envelope = error_data.get("error")
        source: Dict[str, Any] = envelope if isinstance(envelope, dict) else error_data

        code = source.get("code")
        details = source.get("details")

        message = source.get("message")
        if not isinstance(message, str) or not message:
            message = envelope if isinstance(envelope, str) else None
        if not isinstance(message, str) or not message:
            message = UNKNOWN_ERROR_MESSAGE

        return (
            code if isinstance(code, str) else None,
            message,
            details if isinstance(details, dict) else {},
        )

    def _handle_response(self, response: httpx.Response) -> httpx.Response:
        """Handle HTTP response and raise appropriate exceptions."""
        if response.is_success:
            return response

        status_code = response.status_code
        try:
            error_data = response.json()
        except Exception:
            error_data = {"error": response.text}

        code, message, details = self._parse_error_envelope(error_data)
        error_class = _error_class(status_code, code)
        if error_class is AraraError:
            message = f"HTTP {status_code}: {message}"
        raise error_class(
            message,
            status_code,
            error_data,
            code=code,
            details=details,
            retry_after=self._parse_retry_after(response),
        )

    def _parse_body(
        self,
        response: httpx.Response,
        response_model: Optional[Type[T]],
    ) -> Union[T, Dict[str, Any], None]:
        """Deserialize the response body into the requested model or dict."""
        if response.status_code == 204 or not response.content:
            return None
        if response_model:
            return response_model.model_validate(response.json())
        return response.json()

    def _config_for(self, method: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Build the tenacity config for one call, gating retry by method."""
        config = dict(self._retry_config)
        config["retry"] = _retry_policy(method, kwargs.get("headers"))
        return config

    def _send(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Send a synchronous request and raise for error statuses."""
        response = self.sync_client.request(method, path, **kwargs)
        return self._handle_response(response)

    async def _asend(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Send an asynchronous request and raise for error statuses."""
        response = await self.async_client.request(method, path, **kwargs)
        return self._handle_response(response)

    def request(
        self,
        method: str,
        path: str,
        response_model: Optional[Type[T]] = None,
        **kwargs: Any,
    ) -> Union[T, Dict[str, Any], None]:
        """Send a request, retrying timeouts, connection errors, 5xx and 429.

        POST/PATCH are retried only when they carry an Idempotency-Key.
        """
        try:
            response = Retrying(**self._config_for(method, kwargs))(
                self._send, method, path, **kwargs
            )
        except httpx.TimeoutException as e:
            raise AraraTimeoutError("Request timed out") from e
        except httpx.RequestError as e:
            raise AraraConnectionError(f"Connection error: {str(e)}") from e
        return self._parse_body(response, response_model)

    async def arequest(
        self,
        method: str,
        path: str,
        response_model: Optional[Type[T]] = None,
        **kwargs: Any,
    ) -> Union[T, Dict[str, Any], None]:
        """Send an async request, retrying timeouts, connection errors, 5xx and 429."""
        try:
            response = await AsyncRetrying(**self._config_for(method, kwargs))(
                self._asend, method, path, **kwargs
            )
        except httpx.TimeoutException as e:
            raise AraraTimeoutError("Request timed out") from e
        except httpx.RequestError as e:
            raise AraraConnectionError(f"Connection error: {str(e)}") from e
        return self._parse_body(response, response_model)

    def close(self) -> None:
        """Close the synchronous client."""
        self.sync_client.close()

    async def aclose(self) -> None:
        """Close the asynchronous client."""
        await self.async_client.aclose()
