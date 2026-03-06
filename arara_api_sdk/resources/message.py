from typing import Optional
from arara_api_sdk.resources import BaseResource
from arara_api_sdk.models.message import SendMessageRequest, MessageResponse

class MessageResource(BaseResource):
    """Resource for managing messages."""

    def send(self, request: SendMessageRequest) -> MessageResponse:
        """Sends a message synchronously.

        Args:
            request: The message data including receiver and body/template.

        Returns:
            The API response containing message status and ID.
        """
        return self._http.request(
            "POST", "/v1/messages", 
            response_model=MessageResponse, 
            json=request.model_dump(by_alias=True, exclude_none=True)
        )

    async def send_async(self, request: SendMessageRequest) -> MessageResponse:
        """Sends a message asynchronously.

        Args:
            request: The message data including receiver and body/template.

        Returns:
            The API response containing message status and ID.
        """
        return await self._http.arequest(
            "POST", "/v1/messages", 
            response_model=MessageResponse, 
            json=request.model_dump(by_alias=True, exclude_none=True)
        )

    def get(self, internal_id: str) -> MessageResponse:
        """Retrieves message details synchronously.

        Args:
            internal_id: The Arara internal ID of the message.

        Returns:
            The message details.
        """
        return self._http.request(
            "GET", f"/v1/messages/{internal_id}", 
            response_model=MessageResponse
        )

    async def get_async(self, internal_id: str) -> MessageResponse:
        """Retrieves message details asynchronously.

        Args:
            internal_id: The Arara internal ID of the message.

        Returns:
            The message details.
        """
        return await self._http.arequest(
            "GET", f"/v1/messages/{internal_id}", 
            response_model=MessageResponse
        )
