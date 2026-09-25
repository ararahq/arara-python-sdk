from typing import Any, Dict, Optional
from urllib.parse import quote

from arara_api_sdk.resources import BaseResource

_OPT_OUTS = "/v1/opt-outs"


def _phone_path(phone: str) -> str:
    """Build ``/v1/opt-outs/{phone}`` with the phone URL-encoded (``+`` included)."""
    return f"{_OPT_OUTS}/{quote(phone, safe='')}"


def _create_body(phone: str, reason: Optional[str]) -> Dict[str, Any]:
    """Build the body of ``POST /v1/opt-outs``."""
    body: Dict[str, Any] = {"phone": phone}
    if reason:
        body["reason"] = reason
    return body


class OptOutResource(BaseResource):
    """Numbers that asked not to receive messages (blocked at send time)."""

    def list(self) -> Dict[str, Any]:
        """GET /v1/opt-outs — the organization's opt-out list."""
        return self._http.request("GET", _OPT_OUTS)

    async def list_async(self) -> Dict[str, Any]:
        """GET /v1/opt-outs — asynchronously."""
        return await self._http.arequest("GET", _OPT_OUTS)

    def create(self, phone: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """POST /v1/opt-outs — blocks a number."""
        return self._http.request("POST", _OPT_OUTS, json=_create_body(phone, reason))

    async def create_async(
        self, phone: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """POST /v1/opt-outs — asynchronously."""
        return await self._http.arequest(
            "POST", _OPT_OUTS, json=_create_body(phone, reason)
        )

    def get(self, phone: str) -> Dict[str, Any]:
        """GET /v1/opt-outs/{phone} — opt-out status of one number."""
        return self._http.request("GET", _phone_path(phone))

    async def get_async(self, phone: str) -> Dict[str, Any]:
        """GET /v1/opt-outs/{phone} — asynchronously."""
        return await self._http.arequest("GET", _phone_path(phone))

    def delete(self, phone: str) -> None:
        """DELETE /v1/opt-outs/{phone} — lifts the block."""
        self._http.request("DELETE", _phone_path(phone))

    async def delete_async(self, phone: str) -> None:
        """DELETE /v1/opt-outs/{phone} — asynchronously."""
        await self._http.arequest("DELETE", _phone_path(phone))
