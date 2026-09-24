import httpx
import pytest

from arara_api_sdk.exceptions import (
    AraraApiError,
    AraraAuthError,
    AraraError,
    AraraForbiddenError,
    AraraPlanFeatureLockedError,
    AraraUnprocessableError,
    AraraRateLimitError,
    AraraResourceNotFoundError,
    AraraValidationError,
)


def test_http_client_headers_sent_correctly(http_client, respx_mock):
    """Test that the HttpClient sends correct headers in the request."""
    # Arrange
    respx_mock.get("https://api.arara.test/test").mock(
        return_value=httpx.Response(200, json={"status": "ok"})
    )

    # Act
    http_client.request("GET", "/test")

    # Assert
    request = respx_mock.calls[0].request
    assert request.headers["Authorization"] == f"Bearer {http_client.config.api_key}"
    assert request.headers["Content-Type"] == "application/json"
    assert "Arara-Python-SDK" in request.headers["User-Agent"]

@pytest.mark.asyncio
async def test_http_client_async_request_success(http_client, respx_mock):
    """Test a successful asynchronous request."""
    # Arrange
    respx_mock.get("https://api.arara.test/async-test").mock(
        return_value=httpx.Response(200, json={"status": "async-ok"})
    )

    # Act
    response = await http_client.arequest("GET", "/async-test")

    # Assert
    assert response == {"status": "async-ok"}

def test_http_client_raises_auth_error_on_401(http_client, respx_mock):
    """Test that 401 response raises AraraAuthError."""
    # Arrange
    respx_mock.get("https://api.arara.test/401").mock(
        return_value=httpx.Response(401, json={"error": "Unauthorized"})
    )

    # Act & Assert
    with pytest.raises(AraraAuthError) as exc:
        http_client.request("GET", "/401")
    assert exc.value.status_code == 401

def test_http_client_raises_validation_error_on_400(http_client, respx_mock):
    """Test that 400 response raises AraraValidationError."""
    # Arrange
    respx_mock.get("https://api.arara.test/400").mock(
        return_value=httpx.Response(400, json={"error": "Bad Request"})
    )

    # Act & Assert
    with pytest.raises(AraraValidationError) as exc:
        http_client.request("GET", "/400")
    assert exc.value.status_code == 400

def test_http_client_raises_not_found_on_404(http_client, respx_mock):
    """Test that 404 response raises AraraResourceNotFoundError."""
    # Arrange
    respx_mock.get("https://api.arara.test/404").mock(
        return_value=httpx.Response(404, json={"error": "Not Found"})
    )

    # Act & Assert
    with pytest.raises(AraraResourceNotFoundError) as exc:
        http_client.request("GET", "/404")
    assert exc.value.status_code == 404

def throttled(retry_after=None):
    """Build a 429 response carrying the Arara error envelope."""
    headers = {"Retry-After": retry_after} if retry_after else {}
    return httpx.Response(
        429, headers=headers, json={"error": {"code": "RATE_LIMITED"}}
    )

@pytest.fixture
def recorded_sleeps(http_client):
    """Replace tenacity's sleep so retry waits are recorded instead of slept."""
    sleeps = []
    http_client._retry_config["sleep"] = sleeps.append
    return sleeps

def test_http_client_retries_on_429_waiting_the_retry_after_header(
    http_client, respx_mock, recorded_sleeps
):
    """Test that a 429 is retried after the delay the server asked for."""
    # Arrange
    route = respx_mock.get("https://api.arara.test/429").mock(side_effect=[
        throttled(retry_after="7"),
        httpx.Response(200, json={"status": "ok-after-throttle"})
    ])

    # Act
    response = http_client.request("GET", "/429")

    # Assert
    assert response == {"status": "ok-after-throttle"}
    assert route.call_count == 2
    assert recorded_sleeps == [7.0]

def test_http_client_retries_on_429_with_backoff_when_no_retry_after(
    http_client, respx_mock, recorded_sleeps
):
    """Test that a 429 without Retry-After falls back to exponential backoff."""
    # Arrange
    route = respx_mock.get("https://api.arara.test/429-no-header").mock(side_effect=[
        throttled(),
        httpx.Response(200, json={"status": "ok"})
    ])

    # Act
    response = http_client.request("GET", "/429-no-header")

    # Assert
    assert response == {"status": "ok"}
    assert route.call_count == 2
    assert recorded_sleeps == [2.0]

def test_http_client_raises_rate_limit_error_after_exhausting_retries(
    http_client, respx_mock, recorded_sleeps
):
    """Test that a persistent 429 raises AraraRateLimitError once retries run out."""
    # Arrange
    route = respx_mock.get("https://api.arara.test/429-always").mock(
        return_value=throttled(retry_after="3")
    )

    # Act & Assert
    with pytest.raises(AraraRateLimitError) as exc:
        http_client.request("GET", "/429-always")
    assert route.call_count == http_client.config.max_retries + 1
    assert exc.value.retry_after == 3
    assert exc.value.code == "RATE_LIMITED"

def test_http_client_does_not_retry_429_when_retry_after_exceeds_cap(
    http_client, respx_mock, recorded_sleeps
):
    """Test that an absurd Retry-After surfaces instead of blocking the caller."""
    # Arrange
    route = respx_mock.get("https://api.arara.test/429-long").mock(
        return_value=throttled(retry_after="3600")
    )

    # Act & Assert
    with pytest.raises(AraraRateLimitError) as exc:
        http_client.request("GET", "/429-long")
    assert route.call_count == 1
    assert exc.value.retry_after == 3600
    assert recorded_sleeps == []

@pytest.mark.asyncio
async def test_http_client_async_retries_on_429(http_client, respx_mock):
    """Test that the async path also retries a 429."""
    # Arrange
    async def no_sleep(seconds):
        return None

    http_client._retry_config["sleep"] = no_sleep
    route = respx_mock.get("https://api.arara.test/429-async").mock(side_effect=[
        throttled(retry_after="1"),
        httpx.Response(200, json={"status": "async-ok"})
    ])

    # Act
    response = await http_client.arequest("GET", "/429-async")

    # Assert
    assert response == {"status": "async-ok"}
    assert route.call_count == 2

def test_http_client_extracts_code_message_and_details_from_envelope(
    http_client, respx_mock
):
    """Test that the error envelope is unwrapped into the exception fields."""
    # Arrange
    body = {
        "error": {
            "code": "PLAN_LIMIT_REACHED",
            "message": "Limite do plano atingido em 'numbers': 1/1.",
            "details": {"feature": "numbers", "current": 1, "max": 1},
        }
    }
    respx_mock.get("https://api.arara.test/envelope").mock(
        return_value=httpx.Response(403, json=body)
    )

    # Act & Assert
    with pytest.raises(AraraApiError) as exc:
        http_client.request("GET", "/envelope")
    assert not isinstance(exc.value, AraraForbiddenError)
    assert str(exc.value) == "Limite do plano atingido em 'numbers': 1/1."
    assert exc.value.message == "Limite do plano atingido em 'numbers': 1/1."
    assert exc.value.code == "PLAN_LIMIT_REACHED"
    assert exc.value.details == {"feature": "numbers", "current": 1, "max": 1}

def test_http_client_accepts_legacy_string_error_body(http_client, respx_mock):
    """Test that a bare string error body still yields a string message."""
    # Arrange
    respx_mock.get("https://api.arara.test/legacy").mock(
        return_value=httpx.Response(400, json={"error": "Bad Request"})
    )

    # Act & Assert
    with pytest.raises(AraraValidationError) as exc:
        http_client.request("GET", "/legacy")
    assert str(exc.value) == "Bad Request"
    assert exc.value.code is None
    assert exc.value.details == {}

def test_http_client_falls_back_to_unknown_error_on_non_json_body(
    http_client, respx_mock
):
    """Test that an unparseable body does not leak a dict as the message."""
    # Arrange
    respx_mock.get("https://api.arara.test/html").mock(
        return_value=httpx.Response(404, text="<html>504 Gateway Time-out</html>")
    )

    # Act & Assert
    with pytest.raises(AraraResourceNotFoundError) as exc:
        http_client.request("GET", "/html")
    assert str(exc.value) == "<html>504 Gateway Time-out</html>"

def test_http_client_retry_logic_on_server_error(http_client, respx_mock):
    """Test that the client retries on 500 server errors."""
    # Arrange
    # Mocking two failures and then success
    route = respx_mock.get("https://api.arara.test/retry").mock(side_effect=[
        httpx.Response(500),
        httpx.Response(500),
        httpx.Response(200, json={"status": "ok-after-retry"})
    ])

    # Act
    response = http_client.request("GET", "/retry")

    # Assert
    assert response == {"status": "ok-after-retry"}
    assert route.call_count == 3


def test_http_client_raises_plan_feature_locked_with_upgrade_details(
    http_client, respx_mock
):
    """Test that 403 PLAN_FEATURE_LOCKED becomes a typed error, not an auth error."""
    body = {
        "error": {
            "code": "PLAN_FEATURE_LOCKED",
            "message": "Essa feature esta liberada a partir do plano Voo.",
            "details": {
                "feature": "campaigns",
                "currentPlan": "DECOLAGEM",
                "upgradeTo": "VOO",
            },
        }
    }
    respx_mock.get("https://api.arara.test/locked").mock(
        return_value=httpx.Response(403, json=body)
    )

    with pytest.raises(AraraPlanFeatureLockedError) as exc:
        http_client.request("GET", "/locked")
    assert exc.value.status_code == 403
    assert exc.value.feature == "campaigns"
    assert exc.value.current_plan == "DECOLAGEM"
    assert exc.value.upgrade_to == "VOO"
    assert not isinstance(exc.value, AraraAuthError)
    assert isinstance(exc.value, AraraApiError)


def test_http_client_maps_spring_403_body_to_forbidden_not_auth(
    http_client, respx_mock
):
    """Test that the key filter's Spring 403 body is a forbidden error, not auth."""
    body = {
        "timestamp": "2026-09-24T12:00:00.000+00:00",
        "status": 403,
        "error": "Forbidden",
        "path": "/v1/contacts",
    }
    respx_mock.get("https://api.arara.test/v1/contacts").mock(
        return_value=httpx.Response(403, json=body)
    )

    with pytest.raises(AraraForbiddenError) as exc:
        http_client.request("GET", "/v1/contacts")
    assert not isinstance(exc.value, AraraAuthError)
    assert exc.value.status_code == 403
    assert exc.value.code is None
    assert str(exc.value) == "Forbidden"


def test_http_client_maps_empty_403_to_forbidden(http_client, respx_mock):
    """Test that a 403 with empty body (path outside allowlist) is forbidden."""
    respx_mock.get("https://api.arara.test/bare-403").mock(
        return_value=httpx.Response(403)
    )

    with pytest.raises(AraraForbiddenError) as exc:
        http_client.request("GET", "/bare-403")
    assert exc.value.code is None


def test_http_client_raises_unprocessable_on_422_preflight(http_client, respx_mock):
    """Test that a 422 send pre-flight rejection keeps its code."""
    body = {"error": {"code": "INVALID_RECIPIENT", "message": "Numero invalido"}}
    respx_mock.get("https://api.arara.test/422").mock(
        return_value=httpx.Response(422, json=body)
    )

    with pytest.raises(AraraUnprocessableError) as exc:
        http_client.request("GET", "/422")
    assert exc.value.code == "INVALID_RECIPIENT"


def test_http_client_keeps_generic_error_for_unmapped_status(http_client, respx_mock):
    """Test that an unmapped status still raises AraraError with the status."""
    respx_mock.get("https://api.arara.test/402").mock(
        return_value=httpx.Response(
            402, json={"error": {"code": "INSUFFICIENT_FUNDS", "message": "Sem saldo"}}
        )
    )

    with pytest.raises(AraraError) as exc:
        http_client.request("GET", "/402")
    assert str(exc.value) == "HTTP 402: Sem saldo"
    assert exc.value.code == "INSUFFICIENT_FUNDS"


def test_http_client_does_not_retry_post_without_idempotency_key(
    http_client, respx_mock, recorded_sleeps
):
    """Test that a POST without Idempotency-Key is never retried."""
    route = respx_mock.post("https://api.arara.test/post").mock(
        return_value=httpx.Response(500)
    )

    with pytest.raises(AraraError):
        http_client.request("POST", "/post", json={})
    assert route.call_count == 1


def test_http_client_retries_post_with_idempotency_key_reusing_it(
    http_client, respx_mock, recorded_sleeps
):
    """Test that a POST with Idempotency-Key retries and sends the same key."""
    route = respx_mock.post("https://api.arara.test/post-key").mock(
        side_effect=[httpx.Response(503), httpx.Response(200, json={"ok": True})]
    )

    response = http_client.request(
        "POST", "/post-key", json={}, headers={"Idempotency-Key": "k-1"}
    )

    assert response == {"ok": True}
    assert route.call_count == 2
    keys = [call.request.headers["Idempotency-Key"] for call in route.calls]
    assert keys == ["k-1", "k-1"]


def test_http_client_returns_none_for_empty_success_body(http_client, respx_mock):
    """Test that a 200 with an empty body (Void endpoints) yields None."""
    respx_mock.post("https://api.arara.test/void").mock(
        return_value=httpx.Response(200)
    )

    assert http_client.request("POST", "/void") is None


@pytest.mark.parametrize("blank", ["", " ", "\t", "  \n"])
def test_http_client_does_not_retry_post_with_blank_idempotency_key(
    http_client, respx_mock, recorded_sleeps, blank
):
    """Test that a whitespace-only Idempotency-Key does not unlock POST retries."""
    route = respx_mock.post("https://api.arara.test/post-blank").mock(
        return_value=httpx.Response(503)
    )

    with pytest.raises(AraraError):
        http_client.request(
            "POST", "/post-blank", json={}, headers={"Idempotency-Key": blank}
        )
    assert route.call_count == 1
