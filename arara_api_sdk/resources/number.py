from typing import Any, Dict, List

from arara_api_sdk.resources import BaseResource
from arara_api_sdk.models.number import (
    NumbersResponseDTO,
    RequestNumberRequest,
    UpdateNumberRequest,
)

_BASE = "/v1/organizations/me/numbers"


class NumberResource(BaseResource):
    """Resource for managing the organization's phone numbers."""

    def list(self) -> NumbersResponseDTO:
        """GET /v1/organizations/me/numbers — numbers + slot synchronously."""
        return self._http.request("GET", _BASE, response_model=NumbersResponseDTO)

    async def list_async(self) -> NumbersResponseDTO:
        """GET /v1/organizations/me/numbers — numbers + slot asynchronously."""
        return await self._http.arequest(
            "GET", _BASE, response_model=NumbersResponseDTO
        )

    def update(self, number_id: str, request: UpdateNumberRequest) -> Dict[str, Any]:
        """PATCH /v1/organizations/me/numbers/{id} — updates synchronously."""
        return self._http.request(
            "PATCH", f"{_BASE}/{number_id}",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

    async def update_async(
        self, number_id: str, request: UpdateNumberRequest
    ) -> Dict[str, Any]:
        """PATCH /v1/organizations/me/numbers/{id} — updates asynchronously."""
        return await self._http.arequest(
            "PATCH", f"{_BASE}/{number_id}",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

    def delete(self, number_id: str) -> Dict[str, Any]:
        """DELETE /v1/organizations/me/numbers/{id} — soft delete synchronously."""
        return self._http.request("DELETE", f"{_BASE}/{number_id}")

    async def delete_async(self, number_id: str) -> Dict[str, Any]:
        """DELETE /v1/organizations/me/numbers/{id} — soft delete asynchronously."""
        return await self._http.arequest("DELETE", f"{_BASE}/{number_id}")

    def request(self, request: RequestNumberRequest) -> Dict[str, Any]:
        """POST /v1/organizations/me/numbers/request — asks for one synchronously."""
        return self._http.request(
            "POST", f"{_BASE}/request",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

    async def request_async(self, request: RequestNumberRequest) -> Dict[str, Any]:
        """POST /v1/organizations/me/numbers/request — asks for one asynchronously."""
        return await self._http.arequest(
            "POST", f"{_BASE}/request",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

    def list_requests(self) -> List[Dict[str, Any]]:
        """GET /v1/organizations/me/numbers/requests — pending asks synchronously."""
        return self._http.request("GET", f"{_BASE}/requests")

    async def list_requests_async(self) -> List[Dict[str, Any]]:
        """GET /v1/organizations/me/numbers/requests — pending asks asynchronously."""
        return await self._http.arequest("GET", f"{_BASE}/requests")

    def sync(self, number_id: str) -> Dict[str, Any]:
        """POST /v1/organizations/me/numbers/{id}/sync — health sync synchronously."""
        return self._http.request("POST", f"{_BASE}/{number_id}/sync")

    async def sync_async(self, number_id: str) -> Dict[str, Any]:
        """POST /v1/organizations/me/numbers/{id}/sync — health sync asynchronously."""
        return await self._http.arequest("POST", f"{_BASE}/{number_id}/sync")

    def warming(self, number_id: str) -> Dict[str, Any]:
        """GET /v1/organizations/me/numbers/{id}/warming — pacing synchronously."""
        return self._http.request("GET", f"{_BASE}/{number_id}/warming")

    async def warming_async(self, number_id: str) -> Dict[str, Any]:
        """GET /v1/organizations/me/numbers/{id}/warming — pacing asynchronously."""
        return await self._http.arequest("GET", f"{_BASE}/{number_id}/warming")
