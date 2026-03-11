import pytest
from pydantic import ValidationError
from arara_api_sdk.config import SDKConfig

def test_config_initialization_with_valid_data():
    """Test that SDKConfig initializes correctly with valid data."""
    # Arrange & Act
    config = SDKConfig(api_key="test_key", base_url="https://api.test.com")
    
    # Assert
    assert config.api_key == "test_key"
    assert config.base_url == "https://api.test.com"
    assert config.timeout == 30.0  # default
    assert config.max_retries == 3  # default

def test_config_validation_error_when_missing_required_fields():
    """Test that SDKConfig raises ValidationError when missing required fields."""
    # Arrange & Act & Assert
    with pytest.raises(ValidationError):
        # api_key is required
        SDKConfig(base_url="https://api.test.com")

def test_config_default_values():
    """Test that SDKConfig applies correct default values."""
    # Arrange & Act
    config = SDKConfig(api_key="test_key")
    
    # Assert
    assert config.base_url == "https://api.arara.io"
    assert config.timeout == 30.0
    assert config.max_retries == 3
