import pytest
import respx
import httpx
from arara_api_sdk.http.client import HttpClient
from arara_api_sdk.exceptions import (
    AraraAuthError,
    AraraValidationError,
    AraraRateLimitError,
    AraraResourceNotFoundError,
    AraraServerError,
    AraraTimeoutError
)

def test_http_client_headers_sent_correctly(http_client, respx_mock):
    """Test that the HttpClient sends correct headers in the request."""
    # Arrange
    respx_mock.get("https://api.arara.test/test").mock(return_value=httpx.Response(200, json={"status": "ok"}))
    
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
    respx_mock.get("https://api.arara.test/async-test").mock(return_value=httpx.Response(200, json={"status": "async-ok"}))
    
    # Act
    response = await http_client.arequest("GET", "/async-test")
    
    # Assert
    assert response == {"status": "async-ok"}

def test_http_client_raises_auth_error_on_401(http_client, respx_mock):
    """Test that 401 response raises AraraAuthError."""
    # Arrange
    respx_mock.get("https://api.arara.test/401").mock(return_value=httpx.Response(401, json={"error": "Unauthorized"}))
    
    # Act & Assert
    with pytest.raises(AraraAuthError) as exc:
        http_client.request("GET", "/401")
    assert exc.value.status_code == 401

def test_http_client_raises_validation_error_on_400(http_client, respx_mock):
    """Test that 400 response raises AraraValidationError."""
    # Arrange
    respx_mock.get("https://api.arara.test/400").mock(return_value=httpx.Response(400, json={"error": "Bad Request"}))
    
    # Act & Assert
    with pytest.raises(AraraValidationError) as exc:
        http_client.request("GET", "/400")
    assert exc.value.status_code == 400

def test_http_client_raises_not_found_on_404(http_client, respx_mock):
    """Test that 404 response raises AraraResourceNotFoundError."""
    # Arrange
    respx_mock.get("https://api.arara.test/404").mock(return_value=httpx.Response(404, json={"error": "Not Found"}))
    
    # Act & Assert
    with pytest.raises(AraraResourceNotFoundError) as exc:
        http_client.request("GET", "/404")
    assert exc.value.status_code == 404

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
