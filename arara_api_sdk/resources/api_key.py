from typing import List

from arara_api_sdk.resources import BaseResource
from arara_api_sdk.models.api_key import ApiKey, GeneratedApiKey

_BASE = "/v1/api-keys"


class ApiKeyResource(BaseResource):
    """Resource for managing API keys.

    Read keys only GET; send keys GET plus POST on /messages and /campaigns;
    everything else needs an admin-scoped key.
    """

    def list(self) -> List[ApiKey]:
        """GET /v1/api-keys — lists API keys synchronously."""
        response = self._http.request("GET", _BASE)
        return [ApiKey.model_validate(item) for item in response]

    async def list_async(self) -> List[ApiKey]:
        """GET /v1/api-keys — lists API keys asynchronously."""
        response = await self._http.arequest("GET", _BASE)
        return [ApiKey.model_validate(item) for item in response]

    def create(self, mode: str = "LIVE") -> GeneratedApiKey:
        """POST /v1/api-keys — creates an API key synchronously."""
        return self._http.request(
            "POST", _BASE, response_model=GeneratedApiKey, params={"mode": mode}
        )

    async def create_async(self, mode: str = "LIVE") -> GeneratedApiKey:
        """POST /v1/api-keys — creates an API key asynchronously."""
        return await self._http.arequest(
            "POST", _BASE, response_model=GeneratedApiKey, params={"mode": mode}
        )
