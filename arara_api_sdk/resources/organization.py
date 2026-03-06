from typing import List, Dict, Any, Optional
from arara_api_sdk.resources import BaseResource
from arara_api_sdk.models.organization import (
    OrganizationBrainConfig,
    UpdateBrainConfigRequest,
    WebhookConfig,
    UpdateWebhookRequest,
    InviteUserRequest,
    InvitationResponse,
    OrganizationNumber,
    UpdateNumberRequest
)
from arara_api_sdk.models.auth import UserResponseDTO

class OrganizationResource(BaseResource):
    """Resource for managing organization settings and members."""

    def get_webhook(self) -> WebhookConfig:
        """Retrieves current webhook configuration synchronously.

        Returns:
            The webhook configuration including URL and secret.
        """
        return self._http.request("GET", "/organizations/me/webhook", response_model=WebhookConfig)

    async def get_webhook_async(self) -> WebhookConfig:
        """Retrieves current webhook configuration asynchronously.

        Returns:
            The webhook configuration including URL and secret.
        """
        return await self._http.arequest("GET", "/organizations/me/webhook", response_model=WebhookConfig)

    def update_webhook(self, request: UpdateWebhookRequest) -> Dict[str, Any]:
        """Updates webhook configuration synchronously.

        Args:
            request: The new webhook URL and/or secret.

        Returns:
            The API response confirmation.
        """
        return self._http.request("PATCH", "/organizations/me/webhook", json=request.model_dump(exclude_none=True))

    async def update_webhook_async(self, request: UpdateWebhookRequest) -> Dict[str, Any]:
        """Updates webhook configuration asynchronously.

        Args:
            request: The new webhook URL and/or secret.

        Returns:
            The API response confirmation.
        """
        return await self._http.arequest("PATCH", "/organizations/me/webhook", json=request.model_dump(exclude_none=True))

    def get_brain_config(self) -> OrganizationBrainConfig:
        """Retrieves AI Brain configuration for the organization synchronously.

        Returns:
            The current Brain configuration.
        """
        return self._http.request("GET", "/organizations/me/brain-config", response_model=OrganizationBrainConfig)

    async def get_brain_config_async(self) -> OrganizationBrainConfig:
        """Retrieves AI Brain configuration for the organization asynchronously.

        Returns:
            The current Brain configuration.
        """
        return await self._http.arequest("GET", "/organizations/me/brain-config", response_model=OrganizationBrainConfig)

    def update_brain_config(self, request: UpdateBrainConfigRequest) -> OrganizationBrainConfig:
        """Updates AI Brain configuration synchronously.

        Args:
            request: The new configuration parameters.

        Returns:
            The updated Brain configuration.
        """
        return self._http.request(
            "PATCH", "/organizations/me/brain-config", 
            response_model=OrganizationBrainConfig,
            json=request.model_dump(exclude_none=True)
        )

    async def update_brain_config_async(self, request: UpdateBrainConfigRequest) -> OrganizationBrainConfig:
        """Updates AI Brain configuration asynchronously.

        Args:
            request: The new configuration parameters.

        Returns:
            The updated Brain configuration.
        """
        return await self._http.arequest(
            "PATCH", "/organizations/me/brain-config", 
            response_model=OrganizationBrainConfig,
            json=request.model_dump(exclude_none=True)
        )

    def invite_user(self, request: InviteUserRequest) -> InvitationResponse:
        """Invites a new user to the organization synchronously.

        Args:
            request: Invitation details including email and role.

        Returns:
            The invitation response.
        """
        return self._http.request(
            "POST", "/organizations/me/invitations", 
            response_model=InvitationResponse,
            json=request.model_dump()
        )

    async def invite_user_async(self, request: InviteUserRequest) -> InvitationResponse:
        """Invites a new user to the organization asynchronously.

        Args:
            request: Invitation details including email and role.

        Returns:
            The invitation response.
        """
        return await self._http.arequest(
            "POST", "/organizations/me/invitations", 
            response_model=InvitationResponse,
            json=request.model_dump()
        )

    def list_members(self) -> List[UserResponseDTO]:
        """Lists all organization members synchronously.

        Returns:
            A list of organization members.
        """
        response = self._http.request("GET", "/organizations/me/members")
        return [UserResponseDTO.model_validate(item) for item in response]

    async def list_members_async(self) -> List[UserResponseDTO]:
        """Lists all organization members asynchronously.

        Returns:
            A list of organization members.
        """
        response = await self._http.arequest("GET", "/organizations/me/members")
        return [UserResponseDTO.model_validate(item) for item in response]

    def list_numbers(self) -> List[OrganizationNumber]:
        """Lists all phone numbers owned by the organization synchronously.

        Returns:
            A list of phone numbers.
        """
        response = self._http.request("GET", "/organizations/me/numbers")
        return [OrganizationNumber.model_validate(item) for item in response]

    async def list_numbers_async(self) -> List[OrganizationNumber]:
        """Lists all phone numbers owned by the organization asynchronously.

        Returns:
            A list of phone numbers.
        """
        response = await self._http.arequest("GET", "/organizations/me/numbers")
        return [OrganizationNumber.model_validate(item) for item in response]

    def update_number(self, number_id: str, request: UpdateNumberRequest) -> OrganizationNumber:
        """Updates configuration for a specific phone number synchronously.

        Args:
            number_id: The ID of the number to update.
            request: The updated configuration.

        Returns:
            The updated phone number details.
        """
        return self._http.request(
            "PATCH", f"/organizations/me/numbers/{number_id}", 
            response_model=OrganizationNumber,
            json=request.model_dump(exclude_none=True)
        )

    async def update_number_async(self, number_id: str, request: UpdateNumberRequest) -> OrganizationNumber:
        """Updates configuration for a specific phone number asynchronously.

        Args:
            number_id: The ID of the number to update.
            request: The updated configuration.

        Returns:
            The updated phone number details.
        """
        return await self._http.arequest(
            "PATCH", f"/organizations/me/numbers/{number_id}", 
            response_model=OrganizationNumber,
            json=request.model_dump(exclude_none=True)
        )
