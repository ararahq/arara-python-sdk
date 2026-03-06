import pytest
from arara_api_sdk.exceptions import (
    AraraError,
    AraraAuthError,
    AraraValidationError,
    AraraRateLimitError,
    AraraResourceNotFoundError,
    AraraServerError
)

def test_exceptions_hierarchy():
    """Test the inheritance hierarchy of custom exceptions."""
    # Assert
    assert issubclass(AraraAuthError, AraraError)
    assert issubclass(AraraValidationError, AraraError)
    assert issubclass(AraraRateLimitError, AraraError)
    assert issubclass(AraraResourceNotFoundError, AraraError)
    assert issubclass(AraraServerError, AraraError)

def test_exception_message_and_attributes():
    """Test that exceptions store the message and extra attributes correctly."""
    # Arrange
    message = "Unauthorized access"
    status_code = 401
    response_body = {"error": "Invalid token"}
    
    # Act
    exc = AraraAuthError(message, status_code=status_code, response_body=response_body)
    
    # Assert
    assert str(exc) == message
    assert exc.status_code == status_code
    assert exc.response_body == response_body
