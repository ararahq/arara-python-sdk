from typing import Any, Dict, Optional
from uuid import UUID

from arara_api_sdk.models.campaign import (
    CampaignDetailResponse,
    CampaignListResponse,
    CampaignRequest,
    CampaignResponse,
)
from arara_api_sdk.resources import BaseResource, idempotency_headers

_CAMPAIGNS = "/v1/campaigns"
DEFAULT_CAMPAIGN_PAGE_SIZE = 20


def _list_params(page: int, size: int, status: Optional[str]) -> Dict[str, Any]:
    """Build the query string of ``GET /v1/campaigns``."""
    params: Dict[str, Any] = {"page": page, "size": size}
    if status:
        params["status"] = status
    return params


class CampaignResource(BaseResource):
    """Resource for campaigns (template sent to a contact list)."""

    def create(
        self, request: CampaignRequest, idempotency_key: Optional[str] = None
    ) -> CampaignResponse:
        """POST /v1/campaigns — creates a campaign, always with an Idempotency-Key."""
        return self._http.request(
            "POST",
            _CAMPAIGNS,
            response_model=CampaignResponse,
            json=request.model_dump(mode="json", by_alias=True, exclude_none=True),
            headers=idempotency_headers(idempotency_key),
        )

    async def create_async(
        self, request: CampaignRequest, idempotency_key: Optional[str] = None
    ) -> CampaignResponse:
        """POST /v1/campaigns — asynchronous create."""
        return await self._http.arequest(
            "POST",
            _CAMPAIGNS,
            response_model=CampaignResponse,
            json=request.model_dump(mode="json", by_alias=True, exclude_none=True),
            headers=idempotency_headers(idempotency_key),
        )

    def list(
        self,
        page: int = 0,
        size: int = DEFAULT_CAMPAIGN_PAGE_SIZE,
        status: Optional[str] = None,
    ) -> CampaignListResponse:
        """GET /v1/campaigns — one page of campaigns."""
        return self._http.request(
            "GET",
            _CAMPAIGNS,
            response_model=CampaignListResponse,
            params=_list_params(page, size, status),
        )

    async def list_async(
        self,
        page: int = 0,
        size: int = DEFAULT_CAMPAIGN_PAGE_SIZE,
        status: Optional[str] = None,
    ) -> CampaignListResponse:
        """GET /v1/campaigns — one page of campaigns, asynchronously."""
        return await self._http.arequest(
            "GET",
            _CAMPAIGNS,
            response_model=CampaignListResponse,
            params=_list_params(page, size, status),
        )

    def get(self, campaign_id: UUID) -> CampaignDetailResponse:
        """GET /v1/campaigns/{id} — campaign detail."""
        return self._http.request(
            "GET", f"{_CAMPAIGNS}/{campaign_id}", response_model=CampaignDetailResponse
        )

    async def get_async(self, campaign_id: UUID) -> CampaignDetailResponse:
        """GET /v1/campaigns/{id} — campaign detail, asynchronously."""
        return await self._http.arequest(
            "GET", f"{_CAMPAIGNS}/{campaign_id}", response_model=CampaignDetailResponse
        )

    def cancel(self, campaign_id: UUID) -> None:
        """POST /v1/campaigns/{id}/cancel — stops a scheduled or running campaign."""
        self._http.request("POST", f"{_CAMPAIGNS}/{campaign_id}/cancel")

    async def cancel_async(self, campaign_id: UUID) -> None:
        """POST /v1/campaigns/{id}/cancel — asynchronous cancel."""
        await self._http.arequest("POST", f"{_CAMPAIGNS}/{campaign_id}/cancel")
