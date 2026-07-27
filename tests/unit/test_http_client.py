import httpx
import pytest

from arara_api_sdk.exceptions import (
    AraraAuthError,
    AraraError,
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
    with pytest.raises(AraraError) as exc:
        http_client.request("GET", "/envelope")
    assert str(exc.value) == "HTTP 403: Limite do plano atingido em 'numbers': 1/1."
    assert exc.value.message == "HTTP 403: Limite do plano atingido em 'numbers': 1/1."
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
