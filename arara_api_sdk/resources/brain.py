from arara_api_sdk.resources import BaseResource
from arara_api_sdk.models.brain import BrainRequest, BrainResponse

class BrainResource(BaseResource):
    """Resource for interacting with the AI Brain."""

    def prompt(self, request: BrainRequest) -> BrainResponse:
        """Sends a prompt/question to the AI Brain synchronously.

        Args:
            request: The prompt data and optional context.

        Returns:
            The AI response and any identified actions.
        """
        return self._http.request(
            "POST", "/v1/brain", 
            response_model=BrainResponse,
            json=request.model_dump(by_alias=True)
        )

    async def prompt_async(self, request: BrainRequest) -> BrainResponse:
        """Sends a prompt/question to the AI Brain asynchronously.

        Args:
            request: The prompt data and optional context.

        Returns:
            The AI response and any identified actions.
        """
        return await self._http.arequest(
            "POST", "/v1/brain", 
            response_model=BrainResponse,
            json=request.model_dump(by_alias=True)
        )
