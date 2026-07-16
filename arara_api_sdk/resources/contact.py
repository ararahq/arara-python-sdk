from typing import Any, Dict, List, Optional

from arara_api_sdk.resources import BaseResource
from arara_api_sdk.models.contact import (
    ContactMessagesResponse,
    ContactPatchRequest,
    ContactRequest,
    ContactResponse,
    ContactsBatchResponse,
    ContactsListResponse,
    ContactsReactivationResponse,
    ContactsStatsResponse,
)

_BASE = "/v1/contacts"


class ContactResource(BaseResource):
    """Resource for managing contacts."""

    def list(
        self,
        page: int = 0,
        size: int = 20,
        q: Optional[str] = None,
        lifecycle: Optional[str] = None,
    ) -> ContactsListResponse:
        """GET /v1/contacts — lists contacts synchronously."""
        params: Dict[str, Any] = {"page": page, "size": size}
        if q is not None:
            params["q"] = q
        if lifecycle is not None:
            params["lifecycle"] = lifecycle
        return self._http.request(
            "GET", _BASE, response_model=ContactsListResponse, params=params
        )

    async def list_async(
        self,
        page: int = 0,
        size: int = 20,
        q: Optional[str] = None,
        lifecycle: Optional[str] = None,
    ) -> ContactsListResponse:
        """GET /v1/contacts — lists contacts asynchronously."""
        params: Dict[str, Any] = {"page": page, "size": size}
        if q is not None:
            params["q"] = q
        if lifecycle is not None:
            params["lifecycle"] = lifecycle
        return await self._http.arequest(
            "GET", _BASE, response_model=ContactsListResponse, params=params
        )

    def import_batch(self, contacts: List[ContactRequest]) -> ContactsBatchResponse:
        """POST /v1/contacts/batch — imports contacts synchronously."""
        return self._http.request(
            "POST", f"{_BASE}/batch",
            response_model=ContactsBatchResponse,
            json=[c.model_dump(by_alias=True, exclude_none=True) for c in contacts],
        )

    async def import_batch_async(
        self, contacts: List[ContactRequest]
    ) -> ContactsBatchResponse:
        """POST /v1/contacts/batch — imports contacts asynchronously."""
        return await self._http.arequest(
            "POST", f"{_BASE}/batch",
            response_model=ContactsBatchResponse,
            json=[c.model_dump(by_alias=True, exclude_none=True) for c in contacts],
        )

    def stats(self) -> ContactsStatsResponse:
        """GET /v1/contacts/stats — lifecycle counts synchronously."""
        return self._http.request(
            "GET", f"{_BASE}/stats", response_model=ContactsStatsResponse
        )

    async def stats_async(self) -> ContactsStatsResponse:
        """GET /v1/contacts/stats — lifecycle counts asynchronously."""
        return await self._http.arequest(
            "GET", f"{_BASE}/stats", response_model=ContactsStatsResponse
        )

    def reactivation_candidates(self, limit: int = 100) -> ContactsReactivationResponse:
        """GET /v1/contacts/reactivation — dormant candidates synchronously."""
        return self._http.request(
            "GET", f"{_BASE}/reactivation",
            response_model=ContactsReactivationResponse,
            params={"limit": limit},
        )

    async def reactivation_candidates_async(
        self, limit: int = 100
    ) -> ContactsReactivationResponse:
        """GET /v1/contacts/reactivation — dormant candidates asynchronously."""
        return await self._http.arequest(
            "GET", f"{_BASE}/reactivation",
            response_model=ContactsReactivationResponse,
            params={"limit": limit},
        )

    def list_tags(self) -> Dict[str, Any]:
        """GET /v1/contacts/tags — distinct tags synchronously."""
        return self._http.request("GET", f"{_BASE}/tags")

    async def list_tags_async(self) -> Dict[str, Any]:
        """GET /v1/contacts/tags — distinct tags asynchronously."""
        return await self._http.arequest("GET", f"{_BASE}/tags")

    def get(self, phone: str) -> ContactResponse:
        """GET /v1/contacts/{phone} — a single contact synchronously."""
        return self._http.request(
            "GET", f"{_BASE}/{phone}", response_model=ContactResponse
        )

    async def get_async(self, phone: str) -> ContactResponse:
        """GET /v1/contacts/{phone} — a single contact asynchronously."""
        return await self._http.arequest(
            "GET", f"{_BASE}/{phone}", response_model=ContactResponse
        )

    def update(self, phone: str, request: ContactPatchRequest) -> ContactResponse:
        """PATCH /v1/contacts/{phone} — updates a contact synchronously."""
        return self._http.request(
            "PATCH", f"{_BASE}/{phone}",
            response_model=ContactResponse,
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

    async def update_async(
        self, phone: str, request: ContactPatchRequest
    ) -> ContactResponse:
        """PATCH /v1/contacts/{phone} — updates a contact asynchronously."""
        return await self._http.arequest(
            "PATCH", f"{_BASE}/{phone}",
            response_model=ContactResponse,
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

    def messages(self, phone: str, limit: int = 30) -> ContactMessagesResponse:
        """GET /v1/contacts/{phone}/messages — history synchronously."""
        return self._http.request(
            "GET", f"{_BASE}/{phone}/messages",
            response_model=ContactMessagesResponse,
            params={"limit": limit},
        )

    async def messages_async(
        self, phone: str, limit: int = 30
    ) -> ContactMessagesResponse:
        """GET /v1/contacts/{phone}/messages — history asynchronously."""
        return await self._http.arequest(
            "GET", f"{_BASE}/{phone}/messages",
            response_model=ContactMessagesResponse,
            params={"limit": limit},
        )
