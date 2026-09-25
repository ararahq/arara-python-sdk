from typing import Any, Dict, Optional
from uuid import UUID

from arara_api_sdk.models.common import Page
from arara_api_sdk.models.template import (
    CreateTemplateRequest,
    TemplateResponse,
    TemplateStatusResponse,
)
from arara_api_sdk.resources import BaseResource

_TEMPLATES = "/v1/templates"
DEFAULT_TEMPLATE_PAGE_SIZE = 50
DEFAULT_ANALYTICS_PERIOD = "30d"

TemplatePage = Page[TemplateResponse]


def _list_params(
    name: Optional[str], status: Optional[str], page: int, size: int
) -> Dict[str, Any]:
    """Build the query string of ``GET /v1/templates``."""
    params: Dict[str, Any] = {"page": page, "size": size}
    if name:
        params["name"] = name
    if status:
        params["status"] = status
    return params


class TemplateResource(BaseResource):
    """Resource for message templates.

    ``get``, ``get_status``, ``delete`` and ``analytics`` take the template
    ``id`` (UUID). To find a template by name, use ``list(name=...)``.
    """

    def create(self, request: CreateTemplateRequest) -> TemplateResponse:
        """POST /v1/templates — creates and submits a template for approval."""
        return self._http.request(
            "POST",
            _TEMPLATES,
            response_model=TemplateResponse,
            json=request.model_dump(mode="json", by_alias=True, exclude_none=True),
        )

    async def create_async(self, request: CreateTemplateRequest) -> TemplateResponse:
        """POST /v1/templates — asynchronous create."""
        return await self._http.arequest(
            "POST",
            _TEMPLATES,
            response_model=TemplateResponse,
            json=request.model_dump(mode="json", by_alias=True, exclude_none=True),
        )

    def list(
        self,
        name: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 0,
        size: int = DEFAULT_TEMPLATE_PAGE_SIZE,
    ) -> TemplatePage:
        """GET /v1/templates — one page ``{data, pagination}`` of templates."""
        return self._http.request(
            "GET",
            _TEMPLATES,
            response_model=TemplatePage,
            params=_list_params(name, status, page, size),
        )

    async def list_async(
        self,
        name: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 0,
        size: int = DEFAULT_TEMPLATE_PAGE_SIZE,
    ) -> TemplatePage:
        """GET /v1/templates — one page of templates, asynchronously."""
        return await self._http.arequest(
            "GET",
            _TEMPLATES,
            response_model=TemplatePage,
            params=_list_params(name, status, page, size),
        )

    def get(self, template_id: UUID) -> TemplateResponse:
        """GET /v1/templates/{id} — template details."""
        return self._http.request(
            "GET", f"{_TEMPLATES}/{template_id}", response_model=TemplateResponse
        )

    async def get_async(self, template_id: UUID) -> TemplateResponse:
        """GET /v1/templates/{id} — template details, asynchronously."""
        return await self._http.arequest(
            "GET", f"{_TEMPLATES}/{template_id}", response_model=TemplateResponse
        )

    def delete(self, template_id: UUID) -> None:
        """DELETE /v1/templates/{id} — deletes on Meta and locally."""
        self._http.request("DELETE", f"{_TEMPLATES}/{template_id}")

    async def delete_async(self, template_id: UUID) -> None:
        """DELETE /v1/templates/{id} — asynchronous delete."""
        await self._http.arequest("DELETE", f"{_TEMPLATES}/{template_id}")

    def get_status(self, template_id: UUID) -> TemplateStatusResponse:
        """GET /v1/templates/{id}/status — approval status."""
        return self._http.request(
            "GET",
            f"{_TEMPLATES}/{template_id}/status",
            response_model=TemplateStatusResponse,
        )

    async def get_status_async(self, template_id: UUID) -> TemplateStatusResponse:
        """GET /v1/templates/{id}/status — approval status, asynchronously."""
        return await self._http.arequest(
            "GET",
            f"{_TEMPLATES}/{template_id}/status",
            response_model=TemplateStatusResponse,
        )

    def analytics(
        self, template_id: UUID, period: str = DEFAULT_ANALYTICS_PERIOD
    ) -> Dict[str, Any]:
        """GET /v1/templates/{id}/analytics — delivery and read stats."""
        return self._http.request(
            "GET", f"{_TEMPLATES}/{template_id}/analytics", params={"period": period}
        )

    async def analytics_async(
        self, template_id: UUID, period: str = DEFAULT_ANALYTICS_PERIOD
    ) -> Dict[str, Any]:
        """GET /v1/templates/{id}/analytics — stats, asynchronously."""
        return await self._http.arequest(
            "GET", f"{_TEMPLATES}/{template_id}/analytics", params={"period": period}
        )
