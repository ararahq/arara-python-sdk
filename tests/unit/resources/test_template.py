import pytest
import respx
import httpx
from uuid import uuid4
from arara_api_sdk.models.template import CreateTemplateRequest, TemplateResponse

def test_list_templates_success(arara_client, respx_mock):
    """Test successful template listing."""
    # Arrange
    response_data = [
        {
            "id": str(uuid4()),
            "name": "welcome_msg",
            "formattedName": "welcome_msg",
            "category": "UTILITY",
            "language": "pt_BR",
            "providerName": "TWILIO",
            "providerTemplateId": "HX...",
            "providerStatus": "APPROVED",
            "structureJson": {"body": "Welcome!"},
            "createdAt": "2023-10-27T10:00:00Z"
        }
    ]
    respx_mock.get("https://api.arara.test/v1/templates").mock(return_value=httpx.Response(200, json=response_data))
    
    # Act
    templates = arara_client.templates.list()
    
    # Assert
    assert len(templates) == 1
    assert templates[0].name == "welcome_msg"
    assert isinstance(templates[0], TemplateResponse)

def test_create_template_payload_mapping(arara_client, respx_mock):
    """Test that CreateTemplateRequest maps correctly to the request body."""
    # Arrange
    request = CreateTemplateRequest(
        name="test_template",
        category="MARKETING",
        language="pt_BR",
        structure_json={"body": "Hello {{1}}"}
    )
    respx_mock.post("https://api.arara.test/v1/templates").mock(return_value=httpx.Response(201, json={
        "id": str(uuid4()),
        "name": "test_template",
        "formattedName": "test_template",
        "category": "MARKETING",
        "language": "pt_BR",
        "providerName": "TWILIO",
        "providerTemplateId": "HX...",
        "providerStatus": "PENDING",
        "structureJson": {"body": "Hello {{1}}"},
        "createdAt": "2023-10-27T10:00:00Z"
    }))
    
    # Act
    arara_client.templates.create(request)
    
    # Assert
    last_request = respx_mock.calls[0].request
    assert last_request.method == "POST"
    # Testing camelCase mapping in the body
    import json
    body = json.loads(last_request.content)
    assert "structureJson" in body
    assert body["structureJson"] == {"body": "Hello {{1}}"}
