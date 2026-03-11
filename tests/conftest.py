import pytest
import respx
from arara_api_sdk.config import SDKConfig
from arara_api_sdk.http.client import HttpClient
from arara_api_sdk.client import AraraClient

@pytest.fixture
def mock_api_key():
    return "ara_live_test_key_1234"

@pytest.fixture
def mock_base_url():
    return "https://api.arara.test"

@pytest.fixture
def sdk_config(mock_api_key, mock_base_url):
    return SDKConfig(api_key=mock_api_key, base_url=mock_base_url)

@pytest.fixture
def http_client(sdk_config):
    client = HttpClient(sdk_config)
    yield client
    # Clean up
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(client.aclose())
        else:
            asyncio.run(client.aclose())
    except Exception:
        pass
    client.close()

@pytest.fixture
def arara_client(mock_api_key, mock_base_url):
    with AraraClient(api_key=mock_api_key, base_url=mock_base_url) as client:
        yield client

@pytest.fixture
def respx_mock():
    with respx.mock as mock:
        yield mock
