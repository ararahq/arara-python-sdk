import logging
import time
from typing import Any, Dict, Optional, Type, TypeVar, Union

import httpx
from pydantic import BaseModel, parse_obj_as
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

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

class HttpClient:
    """Internal HTTP client for Arara API with sync and async support."""

    def __init__(self, config: SDKConfig):
        self.config = config
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "User-Agent": "Arara-Python-SDK/0.1.0",
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
            raise AraraRateLimitError(message, status_code, error_data)
        elif 500 <= status_code < 600:
            raise AraraServerError(message, status_code, error_data)
        else:
            raise AraraError(f"HTTP {status_code}: {message}", status_code, error_data)

    @retry(
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException, AraraServerError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def request(
        self,
        method: str,
        path: str,
        response_model: Optional[Type[T]] = None,
        **kwargs,
    ) -> Union[T, Dict[str, Any], None]:
        """Perform a synchronous HTTP request."""
        try:
            response = self.sync_client.request(method, path, **kwargs)
            self._handle_response(response)
            
            if response_model and response.status_code != 204:
                return response_model.model_validate(response.json())
            return response.json() if response.status_code != 204 else None
            
        except httpx.TimeoutException as e:
            raise AraraTimeoutError("Request timed out") from e
        except httpx.RequestError as e:
            raise AraraConnectionError(f"Connection error: {str(e)}") from e

    @retry(
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException, AraraServerError)),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def arequest(
        self,
        method: str,
        path: str,
        response_model: Optional[Type[T]] = None,
        **kwargs,
    ) -> Union[T, Dict[str, Any], None]:
        """Perform an asynchronous HTTP request."""
        try:
            response = await self.async_client.request(method, path, **kwargs)
            self._handle_response(response)
            
            if response_model and response.status_code != 204:
                return response_model.model_validate(response.json())
            return response.json() if response.status_code != 204 else None

        except httpx.TimeoutException as e:
            raise AraraTimeoutError("Request timed out") from e
        except httpx.RequestError as e:
            raise AraraConnectionError(f"Connection error: {str(e)}") from e

    def close(self):
        """Close the synchronous client."""
        self.sync_client.close()

    async def aclose(self):
        """Close the asynchronous client."""
        await self.async_client.aclose()
