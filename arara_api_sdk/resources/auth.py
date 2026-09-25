from arara_api_sdk.models.auth import CurrentUserResponse
from arara_api_sdk.resources import BaseResource

_ME = "/auth/me"


class AuthResource(BaseResource):
    """Identity of the API key. Requires an ADMIN key."""

    def me(self) -> CurrentUserResponse:
        """GET /auth/me — the user that owns the API key."""
        return self._http.request("GET", _ME, response_model=CurrentUserResponse)

    async def me_async(self) -> CurrentUserResponse:
        """GET /auth/me — asynchronously."""
        return await self._http.arequest(
            "GET", _ME, response_model=CurrentUserResponse
        )
