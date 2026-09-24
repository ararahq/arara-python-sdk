import json

import httpx
import pytest

OPT_OUTS = "https://api.arara.test/v1/opt-outs"


def test_auth_me_calls_auth_me_without_v1(arara_client, respx_mock):
    """Test that auth.me() hits GET /auth/me and keeps unknown fields."""
    route = respx_mock.get("https://api.arara.test/auth/me").mock(
        return_value=httpx.Response(
            200,
            json={"name": "Ana", "email": "ana@x.com", "role": "ADMIN", "emailPending": False},
        )
    )

    me = arara_client.auth.me()

    assert route.call_count == 1
    assert me.name == "Ana"
    assert me.role == "ADMIN"


@pytest.mark.asyncio
async def test_auth_me_async(arara_client, respx_mock):
    """Test the async auth.me path."""
    respx_mock.get("https://api.arara.test/auth/me").mock(
        return_value=httpx.Response(200, json={"name": "Ana", "email": "a@x.com"})
    )

    assert (await arara_client.auth.me_async()).email == "a@x.com"


def test_removed_resources_are_gone(arara_client):
    """Test that resources unreachable by API key are no longer exposed."""
    for name in ("payments", "brain", "organizations", "users", "api_keys"):
        assert not hasattr(arara_client, name)


def test_opt_outs_sync_paths(arara_client, respx_mock):
    """Test list, create, get and delete with the phone URL-encoded."""
    respx_mock.get(OPT_OUTS).mock(return_value=httpx.Response(200, json={"items": []}))
    create = respx_mock.post(OPT_OUTS).mock(
        return_value=httpx.Response(201, json={"phone": "+5511987654321"})
    )
    one = respx_mock.get(f"{OPT_OUTS}/%2B5511987654321").mock(
        return_value=httpx.Response(200, json={"optedOut": True})
    )
    delete = respx_mock.delete(f"{OPT_OUTS}/%2B5511987654321").mock(
        return_value=httpx.Response(204)
    )

    assert arara_client.opt_outs.list() == {"items": []}
    arara_client.opt_outs.create("+5511987654321", reason="pediu")
    assert arara_client.opt_outs.get("+5511987654321") == {"optedOut": True}
    assert arara_client.opt_outs.delete("+5511987654321") is None

    assert json.loads(create.calls[0].request.content) == {
        "phone": "+5511987654321",
        "reason": "pediu",
    }
    assert one.call_count == 1
    assert delete.call_count == 1


@pytest.mark.asyncio
async def test_opt_outs_async_paths(arara_client, respx_mock):
    """Test the async opt-out paths; reason is omitted when absent."""
    respx_mock.get(OPT_OUTS).mock(return_value=httpx.Response(200, json={}))
    create = respx_mock.post(OPT_OUTS).mock(return_value=httpx.Response(201, json={}))
    respx_mock.get(f"{OPT_OUTS}/5511").mock(return_value=httpx.Response(200, json={}))
    respx_mock.delete(f"{OPT_OUTS}/5511").mock(return_value=httpx.Response(204))

    assert await arara_client.opt_outs.list_async() == {}
    await arara_client.opt_outs.create_async("5511")
    assert await arara_client.opt_outs.get_async("5511") == {}
    assert await arara_client.opt_outs.delete_async("5511") is None
    assert json.loads(create.calls[0].request.content) == {"phone": "5511"}
