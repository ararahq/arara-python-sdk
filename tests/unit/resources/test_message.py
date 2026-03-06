import pytest
import respx
import httpx
from decimal import Decimal
from arara_api_sdk.models.message import SendMessageRequest, MessageResponse
from arara_api_sdk.exceptions import AraraResourceNotFoundError

def test_send_message_success(arara_client, respx_mock):
    """Test successful message sending."""
    # Arrange
    request = SendMessageRequest(receiver="5511999999999", body="Hello")
    response_data = {
        "id": "msg_123",
        "status": "SENT",
        "mode": "LIVE",
        "receiver": "5511999999999",
        "body": "Hello",
        "cost": "0.05"
    }
    respx_mock.post("https://api.arara.test/v1/messages").mock(return_value=httpx.Response(201, json=response_data))
    
    # Act
    response = arara_client.messages.send(request)
    
    # Assert
    assert isinstance(response, MessageResponse)
    assert response.id == "msg_123"
    assert response.status == "SENT"
    assert response.cost == Decimal("0.05")

def test_get_message_not_found_raises_exception(arara_client, respx_mock):
    """Test that getting a non-existent message raises AraraResourceNotFoundError."""
    # Arrange
    internal_id = "non_existent"
    respx_mock.get(f"https://api.arara.test/v1/messages/{internal_id}").mock(return_value=httpx.Response(404, json={"error": "Not Found"}))
    
    # Act & Assert
    with pytest.raises(AraraResourceNotFoundError):
        arara_client.messages.get(internal_id)

@pytest.mark.asyncio
async def test_send_message_async_success(arara_client, respx_mock):
    """Test successful asynchronous message sending."""
    # Arrange
    request = SendMessageRequest(receiver="5511999999999", body="Hello Async")
    response_data = {
        "id": "msg_async_123",
        "status": "QUEUED",
        "mode": "TEST",
        "receiver": "5511999999999",
        "body": "Hello Async",
        "cost": "0.00"
    }
    respx_mock.post("https://api.arara.test/v1/messages").mock(return_value=httpx.Response(201, json=response_data))
    
    # Act
    response = await arara_client.messages.send_async(request)
    
    # Assert
    assert response.id == "msg_async_123"
    assert response.mode == "TEST"
