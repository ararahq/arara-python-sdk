import json
from decimal import Decimal

import httpx
import pytest
from pydantic import ValidationError

from arara_api_sdk.exceptions import AraraResourceNotFoundError, AraraServerError
from arara_api_sdk.models.message import (
    BatchMessageItem,
    BatchMessageRequest,
    MessageResponse,
    SendMessageRequest,
)

MESSAGES = "https://api.arara.test/v1/messages"
BATCH = "https://api.arara.test/v1/messages/batch"


def accepted(cost="0.05", **extra):
    """Build a MessageResponse body."""
    body = {
        "id": "msg_123",
        "status": "QUEUED",
        "mode": "LIVE",
        "receiver": "5511987654321",
        "cost": cost,
    }
    body.update(extra)
    return body


@pytest.fixture
def no_sleep(arara_client):
    """Skip real backoff sleeps in retry tests."""
    arara_client._http._retry_config["sleep"] = lambda seconds: None


def test_send_message_success(arara_client, respx_mock):
    """Test successful message sending."""
    respx_mock.post(MESSAGES).mock(return_value=httpx.Response(202, json=accepted()))

    response = arara_client.messages.send(
        SendMessageRequest(receiver="+5511987654321", body="Hello")
    )

    assert isinstance(response, MessageResponse)
    assert response.cost == Decimal("0.05")


def test_send_message_accepts_null_cost_and_reason(arara_client, respx_mock):
    """Test that a null cost (TEST mode, scheduled) does not raise after acceptance."""
    respx_mock.post(MESSAGES).mock(
        return_value=httpx.Response(
            202, json=accepted(cost=None, mode="TEST", reason="scheduled")
        )
    )

    response = arara_client.messages.send(
        SendMessageRequest(receiver="11987654321", body="Hi", mode="TEST")
    )

    assert response.cost is None
    assert response.reason == "scheduled"


def test_send_message_always_sends_generated_idempotency_key(arara_client, respx_mock):
    """Test that each send without a caller key gets its own UUID v4 key."""
    route = respx_mock.post(MESSAGES).mock(
        return_value=httpx.Response(202, json=accepted())
    )
    request = SendMessageRequest(receiver="+5511987654321", body="Hi")

    arara_client.messages.send(request)
    arara_client.messages.send(request)

    keys = [call.request.headers["Idempotency-Key"] for call in route.calls]
    assert len(keys[0]) == 36
    assert keys[0] != keys[1]


def test_send_message_retry_after_5xx_reuses_same_key(
    arara_client, respx_mock, no_sleep
):
    """Test that a retry after a 5xx sends the same Idempotency-Key."""
    route = respx_mock.post(MESSAGES).mock(
        side_effect=[httpx.Response(503), httpx.Response(202, json=accepted())]
    )

    arara_client.messages.send(SendMessageRequest(receiver="+5511987654321", body="Hi"))

    keys = [call.request.headers["Idempotency-Key"] for call in route.calls]
    assert route.call_count == 2
    assert keys[0] == keys[1]


@pytest.mark.parametrize("blank", ["", " ", "\t"])
def test_send_message_generates_key_when_caller_key_is_blank(
    arara_client, respx_mock, blank
):
    """Test that a blank caller key is replaced by a generated UUID v4."""
    route = respx_mock.post(MESSAGES).mock(
        return_value=httpx.Response(202, json=accepted())
    )

    arara_client.messages.send(
        SendMessageRequest(receiver="1", body="Hi"), idempotency_key=blank
    )

    assert len(route.calls[0].request.headers["Idempotency-Key"]) == 36


def test_send_message_strips_caller_key(arara_client, respx_mock):
    """Test that surrounding whitespace is stripped from the caller key."""
    route = respx_mock.post(MESSAGES).mock(
        return_value=httpx.Response(202, json=accepted())
    )

    arara_client.messages.send(
        SendMessageRequest(receiver="1", body="Hi"), idempotency_key=" order-7 "
    )

    assert route.calls[0].request.headers["Idempotency-Key"] == "order-7"


def test_send_message_uses_caller_idempotency_key(arara_client, respx_mock):
    """Test that a caller-supplied key is sent as is."""
    route = respx_mock.post(MESSAGES).mock(
        return_value=httpx.Response(202, json=accepted())
    )

    arara_client.messages.send(
        SendMessageRequest(receiver="+5511987654321", body="Hi"),
        idempotency_key="order-42",
    )

    assert route.calls[0].request.headers["Idempotency-Key"] == "order-42"


@pytest.mark.asyncio
async def test_send_message_async_retry_reuses_caller_key(arara_client, respx_mock):
    """Test the async send: retries keep the caller key."""

    async def no_async_sleep(seconds):
        return None

    arara_client._http._retry_config["sleep"] = no_async_sleep
    route = respx_mock.post(MESSAGES).mock(
        side_effect=[httpx.Response(500), httpx.Response(202, json=accepted())]
    )

    response = await arara_client.messages.send_async(
        SendMessageRequest(receiver="+5511987654321", body="Hi"),
        idempotency_key="k-async",
    )

    assert response.id == "msg_123"
    keys = [call.request.headers["Idempotency-Key"] for call in route.calls]
    assert keys == ["k-async", "k-async"]


def test_send_message_raises_after_retries_exhausted(
    arara_client, respx_mock, no_sleep
):
    """Test that persistent 5xx surfaces a server error."""
    respx_mock.post(MESSAGES).mock(return_value=httpx.Response(500))

    with pytest.raises(AraraServerError):
        arara_client.messages.send(SendMessageRequest(receiver="1", body="x"))


def test_send_message_serializes_scheduled_at(arara_client, respx_mock):
    """Test that scheduled_at is sent as ISO-8601 under the snake_case key."""
    route = respx_mock.post(MESSAGES).mock(
        return_value=httpx.Response(202, json=accepted(cost=None))
    )

    arara_client.messages.send(
        SendMessageRequest(
            receiver="1",
            template_name="t",
            template_variables=["a"],
            scheduled_at="2026-12-25T10:00:00Z",
        )
    )

    body = json.loads(route.calls[0].request.content)
    assert body["scheduled_at"].startswith("2026-12-25T10:00:00")
    assert body["variables"] == ["a"]
    assert body["templateName"] == "t"


def test_variables_reject_newlines():
    """Test that variables with newlines are rejected locally."""
    with pytest.raises(ValidationError):
        SendMessageRequest(receiver="1", template_variables=["a\nb"])
    with pytest.raises(ValidationError):
        BatchMessageItem(receiver="1", variables=["a\tb"])


def test_batch_rejects_more_than_1000_messages():
    """Test that the batch limit is enforced before the request."""
    items = [BatchMessageItem(receiver=str(i)) for i in range(1001)]
    with pytest.raises(ValidationError):
        BatchMessageRequest(template_name="t", messages=items)


def test_send_batch_posts_items_with_idempotency_key(arara_client, respx_mock):
    """Test that send_batch posts the template and items with a key."""
    route = respx_mock.post(BATCH).mock(
        return_value=httpx.Response(
            202,
            json={
                "batchId": "b-1",
                "templateName": "t",
                "total": 1,
                "accepted": 1,
                "totalCost": "0.05",
                "messages": [
                    {"id": "msg_123", "receiver": "1", "status": "QUEUED", "cost": "0.05"},
                    {"id": None, "receiver": "2", "status": "FAILED", "cost": None},
                ],
            },
        )
    )

    result = arara_client.messages.send_batch(
        BatchMessageRequest(
            template_name="t",
            messages=[BatchMessageItem(receiver="1", variables=["Ana"])],
        )
    )

    body = json.loads(route.calls[0].request.content)
    assert body == {"templateName": "t", "messages": [{"receiver": "1", "variables": ["Ana"]}]}
    assert route.calls[0].request.headers["Idempotency-Key"]
    assert result.batch_id == "b-1"
    assert result.messages[0].id == "msg_123"
    assert result.messages[1].id is None
    assert result.messages[1].status == "FAILED"
    assert result.messages[1].cost is None


@pytest.mark.asyncio
async def test_send_batch_async_and_list_by_batch(arara_client, respx_mock):
    """Test async batch send and the batch listing paths."""
    respx_mock.post(BATCH).mock(
        return_value=httpx.Response(
            202,
            json={
                "batchId": "b-2",
                "templateName": "t",
                "total": 1,
                "accepted": 0,
                "totalCost": "0",
                "messages": [
                    {"id": None, "receiver": "1", "status": "FAILED", "cost": None}
                ],
            },
        )
    )
    list_route = respx_mock.get(MESSAGES).mock(
        return_value=httpx.Response(200, json=[accepted()])
    )
    request = BatchMessageRequest(
        template_name="t", messages=[BatchMessageItem(receiver="1")]
    )

    result = await arara_client.messages.send_batch_async(request, "k-b")
    listed_sync = arara_client.messages.list_by_batch("b-2")
    listed_async = await arara_client.messages.list_by_batch_async("b-2")

    assert result.batch_id == "b-2"
    assert result.messages[0].id is None
    assert listed_sync[0].id == listed_async[0].id == "msg_123"
    assert list_route.calls[0].request.url.params["batchId"] == "b-2"


def test_get_message_not_found_raises_exception(arara_client, respx_mock):
    """Test that a 404 with empty body raises AraraResourceNotFoundError."""
    respx_mock.get(f"{MESSAGES}/missing").mock(return_value=httpx.Response(404))

    with pytest.raises(AraraResourceNotFoundError):
        arara_client.messages.get("missing")


@pytest.mark.asyncio
async def test_get_message_async(arara_client, respx_mock):
    """Test the async get path."""
    respx_mock.get(f"{MESSAGES}/msg_123").mock(
        return_value=httpx.Response(200, json=accepted())
    )

    assert (await arara_client.messages.get_async("msg_123")).id == "msg_123"
