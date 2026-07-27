import logging
from typing import Any, Dict, Optional, Tuple, Type, TypeVar, Union

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
    AraraAuthError,
    AraraConnectionError,
    AraraError,
    AraraRateLimitError,
    AraraResourceNotFoundError,
    AraraServerError,
    AraraTimeoutError,
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

        if status_code == 401:
            raise AraraAuthError(message, status_code, error_data, code, details)
        elif status_code == 400:
            raise AraraValidationError(message, status_code, error_data, code, details)
        elif status_code == 404:
            raise AraraResourceNotFoundError(
                message, status_code, error_data, code, details
            )
        elif status_code == 429:
            raise AraraRateLimitError(
                message,
                status_code,
                error_data,
                retry_after=self._parse_retry_after(response),
                code=code,
                details=details,
            )
        elif 500 <= status_code < 600:
            raise AraraServerError(message, status_code, error_data, code, details)
        else:
            raise AraraError(
                f"HTTP {status_code}: {message}", status_code, error_data, code, details
            )

    def _parse_body(
        self,
        response: httpx.Response,
        response_model: Optional[Type[T]],
    ) -> Union[T, Dict[str, Any], None]:
        """Deserialize the response body into the requested model or dict."""
        if response.status_code == 204:
            return None
        if response_model:
            return response_model.model_validate(response.json())
        return response.json()

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
        **kwargs,
    ) -> Union[T, Dict[str, Any], None]:
        """Send a request, retrying timeouts, connection errors, 5xx and 429."""
        try:
            response = Retrying(**self._retry_config)(
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
        **kwargs,
    ) -> Union[T, Dict[str, Any], None]:
        """Send an async request, retrying timeouts, connection errors, 5xx and 429."""
        try:
            response = await AsyncRetrying(**self._retry_config)(
                self._asend, method, path, **kwargs
            )
        except httpx.TimeoutException as e:
            raise AraraTimeoutError("Request timed out") from e
        except httpx.RequestError as e:
            raise AraraConnectionError(f"Connection error: {str(e)}") from e
        return self._parse_body(response, response_model)

    def close(self):
        """Close the synchronous client."""
        self.sync_client.close()

    async def aclose(self):
        """Close the asynchronous client."""
        await self.async_client.aclose()
