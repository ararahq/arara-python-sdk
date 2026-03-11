from typing import Dict, Any
from arara_api_sdk.resources import BaseResource
from arara_api_sdk.models.user import UserProfileResponse, UserUpdate

class UserResource(BaseResource):
    """Resource for managing user profile."""

    def me(self) -> UserProfileResponse:
        """Retrieves the current user's profile information synchronously.

        Returns:
            The profile details of the authenticated user.
        """
        return self._http.request("GET", "/users/me", response_model=UserProfileResponse)

    async def me_async(self) -> UserProfileResponse:
        """Retrieves the current user's profile information asynchronously.

        Returns:
            The profile details of the authenticated user.
        """
        return await self._http.arequest("GET", "/users/me", response_model=UserProfileResponse)

    def update(self, request: UserUpdate) -> Dict[str, Any]:
        """Updates the current user's profile synchronously.

        Args:
            request: The updated profile information.

        Returns:
            The API confirmation response.
        """
        return self._http.request("PATCH", "/users/me", json=request.model_dump(exclude_none=True))

    async def update_async(self, request: UserUpdate) -> Dict[str, Any]:
        """Updates the current user's profile asynchronously.

        Args:
            request: The updated profile information.

        Returns:
            The API confirmation response.
        """
        return await self._http.arequest("PATCH", "/users/me", json=request.model_dump(exclude_none=True))
