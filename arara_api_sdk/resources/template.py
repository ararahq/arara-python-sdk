from typing import List, Optional
from uuid import UUID
from arara_api_sdk.resources import BaseResource
from arara_api_sdk.models.template import (
    TemplateResponse, 
    CreateTemplateRequest, 
    TemplateStatusResponse
)

class TemplateResource(BaseResource):
    """Resource for managing templates."""

    def create(self, request: CreateTemplateRequest) -> TemplateResponse:
        """Creates a new message template synchronously.

        Args:
            request: The template creation data.

        Returns:
            The created template details.
        """
        return self._http.request(
            "POST", "/v1/templates",
            response_model=TemplateResponse,
            json=request.model_dump(by_alias=True)
        )

    async def create_async(self, request: CreateTemplateRequest) -> TemplateResponse:
        """Creates a new message template asynchronously.

        Args:
            request: The template creation data.

        Returns:
            The created template details.
        """
        return await self._http.arequest(
            "POST", "/v1/templates",
            response_model=TemplateResponse,
            json=request.model_dump(by_alias=True)
        )

    def list(self, name: Optional[str] = None) -> List[TemplateResponse]:
        """Lists available message templates synchronously.

        Args:
            name: Optional filter by template name.

        Returns:
            A list of templates.
        """
        params = {"name": name} if name else None
        response = self._http.request("GET", "/v1/templates", params=params)
        return [TemplateResponse.model_validate(item) for item in response]

    async def list_async(self, name: Optional[str] = None) -> List[TemplateResponse]:
        """Lists available message templates asynchronously.

        Args:
            name: Optional filter by template name.

        Returns:
            A list of templates.
        """
        params = {"name": name} if name else None
        response = await self._http.arequest("GET", "/v1/templates", params=params)
        return [TemplateResponse.model_validate(item) for item in response]

    def get(self, template_id: UUID) -> TemplateResponse:
        """Retrieves details of a specific template synchronously.

        Args:
            template_id: The unique ID of the template.

        Returns:
            The template details.
        """
        return self._http.request(
            "GET", f"/v1/templates/{template_id}",
            response_model=TemplateResponse
        )

    async def get_async(self, template_id: UUID) -> TemplateResponse:
        """Retrieves details of a specific template asynchronously.

        Args:
            template_id: The unique ID of the template.

        Returns:
            The template details.
        """
        return await self._http.arequest(
            "GET", f"/v1/templates/{template_id}",
            response_model=TemplateResponse
        )

    def delete(self, template_id: UUID) -> None:
        """Deletes a message template synchronously.

        Args:
            template_id: The unique ID of the template to delete.
        """
        self._http.request("DELETE", f"/v1/templates/{template_id}")

    async def delete_async(self, template_id: UUID) -> None:
        """Deletes a message template asynchronously.

        Args:
            template_id: The unique ID of the template to delete.
        """
        await self._http.arequest("DELETE", f"/v1/templates/{template_id}")

    def get_status(self, template_id: UUID) -> TemplateStatusResponse:
        """Checks the status of a template synchronously.

        Args:
            template_id: The unique ID of the template.

        Returns:
            The current approval status of the template.
        """
        return self._http.request(
            "GET", f"/v1/templates/{template_id}/status",
            response_model=TemplateStatusResponse
        )

    async def get_status_async(self, template_id: UUID) -> TemplateStatusResponse:
        """Checks the status of a template asynchronously.

        Args:
            template_id: The unique ID of the template.

        Returns:
            The current approval status of the template.
        """
        return await self._http.arequest(
            "GET", f"/v1/templates/{template_id}/status",
            response_model=TemplateStatusResponse
        )
