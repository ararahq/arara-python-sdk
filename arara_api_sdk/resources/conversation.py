from typing import Any, Dict, List, Optional

from arara_api_sdk.resources import BaseResource
from arara_api_sdk.models.conversation import ConversationReplyRequest

_BASE = "/v1/conversations"


class ConversationResource(BaseResource):
    """Resource for managing inbox conversations."""

    def list(
        self,
        status: Optional[str] = None,
        lead_status: Optional[str] = None,
        page: int = 0,
        size: int = 20,
    ) -> Dict[str, Any]:
        """GET /v1/conversations — lists conversations synchronously."""
        params: Dict[str, Any] = {"page": page, "size": size}
        if status is not None:
            params["status"] = status
        if lead_status is not None:
            params["leadStatus"] = lead_status
        return self._http.request("GET", _BASE, params=params)

    async def list_async(
        self,
        status: Optional[str] = None,
        lead_status: Optional[str] = None,
        page: int = 0,
        size: int = 20,
    ) -> Dict[str, Any]:
        """GET /v1/conversations — lists conversations asynchronously."""
        params: Dict[str, Any] = {"page": page, "size": size}
        if status is not None:
            params["status"] = status
        if lead_status is not None:
            params["leadStatus"] = lead_status
        return await self._http.arequest("GET", _BASE, params=params)

    def lead_stats(self) -> Dict[str, Any]:
        """GET /v1/conversations/lead-stats — lead counts synchronously."""
        return self._http.request("GET", f"{_BASE}/lead-stats")

    async def lead_stats_async(self) -> Dict[str, Any]:
        """GET /v1/conversations/lead-stats — lead counts asynchronously."""
        return await self._http.arequest("GET", f"{_BASE}/lead-stats")

    def messages(
        self, conversation_id: str, page: int = 0, size: int = 50
    ) -> Dict[str, Any]:
        """GET /v1/conversations/{id}/messages — messages synchronously."""
        return self._http.request(
            "GET", f"{_BASE}/{conversation_id}/messages",
            params={"page": page, "size": size},
        )

    async def messages_async(
        self, conversation_id: str, page: int = 0, size: int = 50
    ) -> Dict[str, Any]:
        """GET /v1/conversations/{id}/messages — messages asynchronously."""
        return await self._http.arequest(
            "GET", f"{_BASE}/{conversation_id}/messages",
            params={"page": page, "size": size},
        )

    def reply(self, request: ConversationReplyRequest) -> Dict[str, Any]:
        """POST /v1/conversations/reply — sends a session reply synchronously."""
        return self._http.request(
            "POST", f"{_BASE}/reply", json=request.model_dump(by_alias=True)
        )

    async def reply_async(self, request: ConversationReplyRequest) -> Dict[str, Any]:
        """POST /v1/conversations/reply — sends a session reply asynchronously."""
        return await self._http.arequest(
            "POST", f"{_BASE}/reply", json=request.model_dump(by_alias=True)
        )

    def update_status(self, conversation_id: str, status: str) -> Dict[str, Any]:
        """PATCH /v1/conversations/{id}/status — updates status synchronously."""
        return self._http.request(
            "PATCH", f"{_BASE}/{conversation_id}/status", json={"status": status}
        )

    async def update_status_async(
        self, conversation_id: str, status: str
    ) -> Dict[str, Any]:
        """PATCH /v1/conversations/{id}/status — updates status asynchronously."""
        return await self._http.arequest(
            "PATCH", f"{_BASE}/{conversation_id}/status", json={"status": status}
        )

    def window_status(self, phones: List[str]) -> Dict[str, Any]:
        """POST /v1/conversations/window-status — 24h window check synchronously."""
        return self._http.request(
            "POST", f"{_BASE}/window-status", json={"phones": phones}
        )

    async def window_status_async(self, phones: List[str]) -> Dict[str, Any]:
        """POST /v1/conversations/window-status — 24h window check asynchronously."""
        return await self._http.arequest(
            "POST", f"{_BASE}/window-status", json={"phones": phones}
        )
