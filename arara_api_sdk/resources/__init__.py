from typing import Dict, Optional
from uuid import uuid4

from arara_api_sdk.http.client import IDEMPOTENCY_HEADER, HttpClient


class BaseResource:
    """Base class for all API resources."""

    def __init__(self, http_client: HttpClient):
        """Keep the shared HTTP client."""
        self._http = http_client


def idempotency_headers(idempotency_key: Optional[str]) -> Dict[str, str]:
    """Return the Idempotency-Key header, generating a UUID v4 when absent.

    The key is created once per SDK call and travels unchanged on every retry
    of that call, so a timeout after the API accepted the request does not
    send (and bill) the message twice.
    """
    return {IDEMPOTENCY_HEADER: idempotency_key or str(uuid4())}
