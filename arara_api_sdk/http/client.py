import logging
from typing import Any, Dict, Optional, Type, TypeVar, Union

import httpx
from pydantic import BaseModel
from tenacity import (
    AsyncRetrying,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from arara_api_sdk._version import __version__
from arara_api_sdk.config import SDKConfig
from arara_api_sdk.exceptions import (
    AraraAuthError,
    AraraValidationError,
    AraraRateLimitError,
    AraraResourceNotFoundError,
    AraraServerError,
    AraraConnectionError,
    AraraTimeoutError,
    AraraError,
)

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger("arara_sdk")

RETRYABLE_EXCEPTIONS = (httpx.ConnectError, httpx.TimeoutException, AraraServerError)

class HttpClient:
    """Internal HTTP client for Arara API with sync and async support."""

    def __init__(self, config: SDKConfig):
        self.config = config
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "User-Agent": f"Arara-Python-SDK/{__version__}",
        }
        self._retry_config: Dict[str, Any] = {
            "retry": retry_if_exception_type(RETRYABLE_EXCEPTIONS),
            "wait": wait_exponential(multiplier=1, min=2, max=10),
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
            return int(header)
        except ValueError:
            return None

    def _handle_response(self, response: httpx.Response) -> httpx.Response:
        """Handle HTTP response and raise appropriate exceptions."""
        if response.is_success:
            return response

        status_code = response.status_code
        try:
            error_data = response.json()
        except Exception:
            error_data = {"error": response.text}

        message = error_data.get("error") or error_data.get("message") or "Unknown error"

        if status_code == 401:
            raise AraraAuthError(message, status_code, error_data)
        elif status_code == 400:
            raise AraraValidationError(message, status_code, error_data)
        elif status_code == 404:
            raise AraraResourceNotFoundError(message, status_code, error_data)
        elif status_code == 429:
            raise AraraRateLimitError(
                message,
                status_code,
                error_data,
                retry_after=self._parse_retry_after(response),
            )
        elif 500 <= status_code < 600:
            raise AraraServerError(message, status_code, error_data)
        else:
            raise AraraError(f"HTTP {status_code}: {message}", status_code, error_data)

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
        """Perform a synchronous HTTP request with retries on timeout, connection and 5xx errors."""
        try:
            response = Retrying(**self._retry_config)(self._send, method, path, **kwargs)
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
        """Perform an asynchronous HTTP request with retries on timeout, connection and 5xx errors."""
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
