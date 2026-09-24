from typing import Any, Dict

from arara_api_sdk.models.common import Page
from arara_api_sdk.models.smart_link import (
    CreateWhatsAppSmartLinkRequest,
    UpdateWhatsAppSmartLinkRequest,
    WhatsAppSmartLinkResponse,
)
from arara_api_sdk.resources import BaseResource

_BASE = "/v1/smart-links/whatsapp"
DEFAULT_SMART_LINK_PAGE_SIZE = 50

SmartLinkPage = Page[WhatsAppSmartLinkResponse]


class SmartLinkResource(BaseResource):
    """Resource for managing WhatsApp smart links."""

    def create(
        self, request: CreateWhatsAppSmartLinkRequest
    ) -> WhatsAppSmartLinkResponse:
        """POST /v1/smart-links/whatsapp — creates a smart link synchronously."""
        return self._http.request(
            "POST", _BASE,
            response_model=WhatsAppSmartLinkResponse,
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

    async def create_async(
        self, request: CreateWhatsAppSmartLinkRequest
    ) -> WhatsAppSmartLinkResponse:
        """POST /v1/smart-links/whatsapp — creates a smart link asynchronously."""
        return await self._http.arequest(
            "POST", _BASE,
            response_model=WhatsAppSmartLinkResponse,
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

    def update(
        self, link_id: str, request: UpdateWhatsAppSmartLinkRequest
    ) -> WhatsAppSmartLinkResponse:
        """PUT /v1/smart-links/whatsapp/{id} — updates a smart link synchronously."""
        return self._http.request(
            "PUT", f"{_BASE}/{link_id}",
            response_model=WhatsAppSmartLinkResponse,
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

    async def update_async(
        self, link_id: str, request: UpdateWhatsAppSmartLinkRequest
    ) -> WhatsAppSmartLinkResponse:
        """PUT /v1/smart-links/whatsapp/{id} — updates a smart link asynchronously."""
        return await self._http.arequest(
            "PUT", f"{_BASE}/{link_id}",
            response_model=WhatsAppSmartLinkResponse,
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

    def list(
        self, page: int = 0, size: int = DEFAULT_SMART_LINK_PAGE_SIZE
    ) -> SmartLinkPage:
        """GET /v1/smart-links/whatsapp — one page ``{data, pagination}``."""
        return self._http.request(
            "GET",
            _BASE,
            response_model=SmartLinkPage,
            params={"page": page, "size": size},
        )

    async def list_async(
        self, page: int = 0, size: int = DEFAULT_SMART_LINK_PAGE_SIZE
    ) -> SmartLinkPage:
        """GET /v1/smart-links/whatsapp — one page, asynchronously."""
        return await self._http.arequest(
            "GET",
            _BASE,
            response_model=SmartLinkPage,
            params={"page": page, "size": size},
        )

    def stats(self, link_id: str) -> Dict[str, Any]:
        """GET /v1/smart-links/whatsapp/{id}/stats — click stats synchronously."""
        return self._http.request("GET", f"{_BASE}/{link_id}/stats")

    async def stats_async(self, link_id: str) -> Dict[str, Any]:
        """GET /v1/smart-links/whatsapp/{id}/stats — click stats asynchronously."""
        return await self._http.arequest("GET", f"{_BASE}/{link_id}/stats")
