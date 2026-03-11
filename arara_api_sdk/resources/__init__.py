from typing import Optional
from arara_api_sdk.http.client import HttpClient

class BaseResource:
    """Base class for all API resources."""
    def __init__(self, http_client: HttpClient):
        self._http = http_client
