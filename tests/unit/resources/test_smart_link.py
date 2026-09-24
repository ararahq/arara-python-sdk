from uuid import uuid4

import httpx
import pytest

BASE = "https://api.arara.test/v1/smart-links/whatsapp"


def link():
    """Build a WhatsAppSmartLinkResponse body."""
    return {
        "id": str(uuid4()),
        "name": "Loja",
        "phoneNumber": "5511987654321",
        "qrCodeColor": "BLACK",
        "code": "abc",
        "shortUrl": "https://ararahq.com/l/abc",
    }


def test_list_smart_links_returns_paginated_page(arara_client, respx_mock):
    """Test that list() parses {data, pagination}."""
    route = respx_mock.get(BASE).mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [link()],
                "pagination": {
                    "page": 0,
                    "size": 50,
                    "totalElements": 1,
                    "totalPages": 1,
                },
            },
        )
    )

    page = arara_client.smart_links.list()

    assert page.data[0].code == "abc"
    assert page.pagination.total_pages == 1
    assert route.calls[0].request.url.params["size"] == "50"


@pytest.mark.asyncio
async def test_list_smart_links_async(arara_client, respx_mock):
    """Test the async list path."""
    respx_mock.get(BASE).mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [],
                "pagination": {"page": 3, "size": 1, "totalElements": 0, "totalPages": 0},
            },
        )
    )

    page = await arara_client.smart_links.list_async(page=3, size=1)

    assert page.data == []
    assert page.pagination.page == 3
