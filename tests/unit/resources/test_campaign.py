import json
from uuid import uuid4

import httpx
import pytest

from arara_api_sdk.models.campaign import CampaignContactRequest, CampaignRequest

CAMPAIGNS = "https://api.arara.test/v1/campaigns"
CAMPAIGN_ID = uuid4()


def created():
    """Build a CampaignResponse body."""
    return {
        "id": str(CAMPAIGN_ID),
        "name": "Black Friday",
        "status": "PROCESSING",
        "totalMessages": 2,
        "totalCost": "0.10",
    }


def list_item():
    """Build a CampaignListItem body."""
    return {
        **created(),
        "templateName": "promo",
        "sentCount": 2,
        "deliveredCount": 1,
        "readCount": 0,
        "failedCount": 0,
        "scheduledAt": None,
        "createdAt": "2026-09-24T10:00:00Z",
    }


def request():
    """Build a campaign request."""
    return CampaignRequest(
        name="Black Friday",
        template_name="promo",
        contacts=[CampaignContactRequest(to="+5511987654321", variables=["Ana"])],
    )


def test_create_campaign_sends_generated_key_and_reuses_it_on_retry(
    arara_client, respx_mock
):
    """Test that create always sends a key and a retry after 5xx keeps it."""
    arara_client._http._retry_config["sleep"] = lambda seconds: None
    route = respx_mock.post(CAMPAIGNS).mock(
        side_effect=[httpx.Response(502), httpx.Response(200, json=created())]
    )

    campaign = arara_client.campaigns.create(request())

    keys = [call.request.headers["Idempotency-Key"] for call in route.calls]
    assert len(keys) == 2
    assert keys[0] == keys[1]
    assert campaign.id == CAMPAIGN_ID
    body = json.loads(route.calls[0].request.content)
    assert body["templateName"] == "promo"
    assert body["contacts"] == [{"to": "+5511987654321", "variables": ["Ana"]}]
    assert "scheduledAt" not in body


@pytest.mark.asyncio
async def test_create_campaign_async_uses_caller_key_and_schedule(
    arara_client, respx_mock
):
    """Test that the caller key and scheduledAt are sent."""
    route = respx_mock.post(CAMPAIGNS).mock(
        return_value=httpx.Response(200, json=created())
    )
    scheduled = CampaignRequest(
        name="Agendada",
        template_name="promo",
        contacts=[CampaignContactRequest(to="11987654321")],
        scheduled_at="2026-12-01T12:00:00Z",
    )

    await arara_client.campaigns.create_async(scheduled, idempotency_key="camp-1")

    assert route.calls[0].request.headers["Idempotency-Key"] == "camp-1"
    body = json.loads(route.calls[0].request.content)
    assert body["scheduledAt"].startswith("2026-12-01T12:00:00")


def test_list_campaigns_parses_content_page(arara_client, respx_mock):
    """Test that list() parses {content, totalPages, totalElements}."""
    route = respx_mock.get(CAMPAIGNS).mock(
        return_value=httpx.Response(
            200, json={"content": [list_item()], "totalPages": 1, "totalElements": 1}
        )
    )

    page = arara_client.campaigns.list(status="COMPLETED")

    assert page.total_elements == 1
    assert page.content[0].template_name == "promo"
    assert route.calls[0].request.url.params["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_list_campaigns_async_without_status(arara_client, respx_mock):
    """Test the async list omits status when not given."""
    route = respx_mock.get(CAMPAIGNS).mock(
        return_value=httpx.Response(
            200, json={"content": [], "totalPages": 0, "totalElements": 0}
        )
    )

    page = await arara_client.campaigns.list_async(page=1, size=5)

    assert page.content == []
    params = route.calls[0].request.url.params
    assert "status" not in params
    assert params["size"] == "5"


def test_get_and_cancel_campaign(arara_client, respx_mock):
    """Test detail parsing and cancel with an empty 200 body."""
    detail = {
        **list_item(),
        "clickedCount": 0,
        "convertedCount": 0,
        "convertedValue": "0",
        "blockReasons": [{"motivo": "Opt-out", "quantidade": 1}],
        "startedAt": None,
        "finishedAt": None,
    }
    respx_mock.get(f"{CAMPAIGNS}/{CAMPAIGN_ID}").mock(
        return_value=httpx.Response(200, json=detail)
    )
    cancel = respx_mock.post(f"{CAMPAIGNS}/{CAMPAIGN_ID}/cancel").mock(
        return_value=httpx.Response(200)
    )

    campaign = arara_client.campaigns.get(CAMPAIGN_ID)

    assert campaign.block_reasons[0].quantidade == 1
    assert arara_client.campaigns.cancel(CAMPAIGN_ID) is None
    assert cancel.call_count == 1


@pytest.mark.asyncio
async def test_get_and_cancel_campaign_async(arara_client, respx_mock):
    """Test the async get and cancel paths."""
    respx_mock.get(f"{CAMPAIGNS}/{CAMPAIGN_ID}").mock(
        return_value=httpx.Response(200, json=list_item())
    )
    respx_mock.post(f"{CAMPAIGNS}/{CAMPAIGN_ID}/cancel").mock(
        return_value=httpx.Response(200)
    )

    assert (await arara_client.campaigns.get_async(CAMPAIGN_ID)).name == "Black Friday"
    assert await arara_client.campaigns.cancel_async(CAMPAIGN_ID) is None
