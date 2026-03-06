from arara_api_sdk.resources import BaseResource
from arara_api_sdk.models.campaign import CampaignRequest, CampaignResponse

class CampaignResource(BaseResource):
    """Resource for managing marketing campaigns."""

    def create(self, request: CampaignRequest) -> CampaignResponse:
        """Starts a new marketing campaign synchronously.

        Args:
            request: The campaign details and recipients.

        Returns:
            The created campaign summary.
        """
        return self._http.request(
            "POST", "/v1/campaigns", 
            response_model=CampaignResponse,
            json=request.model_dump(by_alias=True)
        )

    async def create_async(self, request: CampaignRequest) -> CampaignResponse:
        """Starts a new marketing campaign asynchronously.

        Args:
            request: The campaign details and recipients.

        Returns:
            The created campaign summary.
        """
        return await self._http.arequest(
            "POST", "/v1/campaigns", 
            response_model=CampaignResponse,
            json=request.model_dump(by_alias=True)
        )
