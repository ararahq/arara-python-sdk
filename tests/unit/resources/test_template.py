import json
from uuid import uuid4

import httpx
import pytest

from arara_api_sdk.models.template import CreateTemplateRequest, TemplateResponse

BASE = "https://api.arara.test/v1/templates"


def template_payload(name="welcome_msg", status="APPROVED"):
    """Build a TemplateResponse body as the API returns it."""
    return {
        "id": str(uuid4()),
        "name": name,
        "formattedName": name,
        "category": "UTILITY",
        "language": "pt_BR",
        "providerName": "GUPSHUP",
        "providerTemplateId": "gs-1",
        "providerStatus": status,
        "availableForSending": True,
        "structureJson": {"body": "Welcome!"},
        "createdAt": "2026-09-24T10:00:00Z",
    }


def page_of(items, page=0, size=50):
    """Wrap items in the {data, pagination} envelope."""
    return {
        "data": items,
        "pagination": {
            "page": page,
            "size": size,
            "totalElements": len(items),
            "totalPages": 1,
        },
    }


def test_list_templates_returns_paginated_page(arara_client, respx_mock):
    """Test that list() parses {data, pagination} instead of iterating the dict."""
    route = respx_mock.get(BASE).mock(
        return_value=httpx.Response(200, json=page_of([template_payload()]))
    )

    page = arara_client.templates.list(name="welcome_msg", status="APPROVED")

    assert len(page.data) == 1
    assert isinstance(page.data[0], TemplateResponse)
    assert page.data[0].name == "welcome_msg"
    assert page.pagination.total_elements == 1
    params = route.calls[0].request.url.params
    assert params["name"] == "welcome_msg"
    assert params["status"] == "APPROVED"
    assert params["page"] == "0"
    assert params["size"] == "50"


@pytest.mark.asyncio
async def test_list_templates_async_returns_paginated_page(arara_client, respx_mock):
    """Test the async list path with default params."""
    route = respx_mock.get(BASE).mock(
        return_value=httpx.Response(200, json=page_of([], page=2, size=10))
    )

    page = await arara_client.templates.list_async(page=2, size=10)

    assert page.data == []
    assert page.pagination.page == 2
    assert "name" not in route.calls[0].request.url.params


def test_create_template_sends_body_not_structure_json(arara_client, respx_mock):
    """Test that create() sends the fields the API validates (body is required)."""
    route = respx_mock.post(BASE).mock(
        return_value=httpx.Response(201, json=template_payload("pedido"))
    )
    request = CreateTemplateRequest(
        name="pedido",
        category="UTILITY",
        body="Ola {{1}}, seu pedido saiu.",
        footer="Arara",
        samples={"1": "Ana"},
        buttons=[{"type": "URL", "text": "Rastrear", "url": "https://x.y/{{1}}"}],
    )

    created = arara_client.templates.create(request)

    body = json.loads(route.calls[0].request.content)
    assert body["body"] == "Ola {{1}}, seu pedido saiu."
    assert body["language"] == "pt_BR"
    assert body["samples"] == {"1": "Ana"}
    assert body["buttons"][0]["type"] == "URL"
    assert "structureJson" not in body
    assert "headerType" not in body
    assert created.name == "pedido"


@pytest.mark.asyncio
async def test_create_template_async(arara_client, respx_mock):
    """Test the async create path."""
    respx_mock.post(BASE).mock(
        return_value=httpx.Response(201, json=template_payload("x"))
    )

    created = await arara_client.templates.create_async(
        CreateTemplateRequest(name="x", category="UTILITY", body="Oi")
    )

    assert created.name == "x"


def test_template_get_status_delete_and_analytics_use_id(arara_client, respx_mock):
    """Test that get/get_status/delete/analytics address the template by UUID."""
    template_id = uuid4()
    respx_mock.get(f"{BASE}/{template_id}").mock(
        return_value=httpx.Response(200, json=template_payload())
    )
    respx_mock.get(f"{BASE}/{template_id}/status").mock(
        return_value=httpx.Response(200, json={"status": "APPROVED"})
    )
    delete_route = respx_mock.delete(f"{BASE}/{template_id}").mock(
        return_value=httpx.Response(204)
    )
    analytics_route = respx_mock.get(f"{BASE}/{template_id}/analytics").mock(
        return_value=httpx.Response(200, json={"sent": 10})
    )

    assert arara_client.templates.get(template_id).name == "welcome_msg"
    assert arara_client.templates.get_status(template_id).status == "APPROVED"
    assert arara_client.templates.delete(template_id) is None
    assert arara_client.templates.analytics(template_id, period="7d") == {"sent": 10}
    assert delete_route.call_count == 1
    assert analytics_route.calls[0].request.url.params["period"] == "7d"


@pytest.mark.asyncio
async def test_template_async_by_id_paths(arara_client, respx_mock):
    """Test the async get/get_status/delete/analytics paths."""
    template_id = uuid4()
    respx_mock.get(f"{BASE}/{template_id}").mock(
        return_value=httpx.Response(200, json=template_payload())
    )
    respx_mock.get(f"{BASE}/{template_id}/status").mock(
        return_value=httpx.Response(200, json={"status": "PENDING"})
    )
    respx_mock.delete(f"{BASE}/{template_id}").mock(return_value=httpx.Response(204))
    respx_mock.get(f"{BASE}/{template_id}/analytics").mock(
        return_value=httpx.Response(200, json={"read": 3})
    )

    assert (await arara_client.templates.get_async(template_id)).name == "welcome_msg"
    status = await arara_client.templates.get_status_async(template_id)
    assert status.status == "PENDING"
    assert await arara_client.templates.delete_async(template_id) is None
    assert await arara_client.templates.analytics_async(template_id) == {"read": 3}
