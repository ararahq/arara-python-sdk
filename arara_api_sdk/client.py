from typing import Any, Dict, Optional

from arara_api_sdk.config import SDKConfig
from arara_api_sdk.http.client import HttpClient
from arara_api_sdk.resources.auth import AuthResource
from arara_api_sdk.resources.campaign import CampaignResource
from arara_api_sdk.resources.contact import ContactResource
from arara_api_sdk.resources.conversation import ConversationResource
from arara_api_sdk.resources.message import MessageResource
from arara_api_sdk.resources.number import NumberResource
from arara_api_sdk.resources.opt_out import OptOutResource
from arara_api_sdk.resources.smart_link import SmartLinkResource
from arara_api_sdk.resources.template import TemplateResource
from arara_api_sdk.resources.wallet import WalletResource


class AraraClient:
    """Official Arara Python SDK client, sync and async.

    Covers what an API key can reach: messages, templates, campaigns,
    contacts, conversations, numbers, opt-outs, smart links, wallet and
    ``auth.me()``. Contacts, conversations, wallet and ``auth.me`` require an
    ADMIN key.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ) -> None:
        """Initialize the client.

        Args:
            api_key: The Arara API key. Falls back to ``ARARA_API_KEY``.
            base_url: API base URL. Defaults to https://api.ararahq.com.
            timeout: Request timeout in seconds. Defaults to 30.0.
            max_retries: Retries for transient failures. Defaults to 3.

        """
        overrides: Dict[str, Any] = {
            "api_key": api_key,
            "base_url": base_url,
            "timeout": timeout,
            "max_retries": max_retries,
        }
        self.config = SDKConfig(
            **{key: value for key, value in overrides.items() if value is not None}
        )
        self._http = HttpClient(self.config)

        self.auth = AuthResource(self._http)
        self.messages = MessageResource(self._http)
        self.templates = TemplateResource(self._http)
        self.campaigns = CampaignResource(self._http)
        self.contacts = ContactResource(self._http)
        self.conversations = ConversationResource(self._http)
        self.wallet = WalletResource(self._http)
        self.numbers = NumberResource(self._http)
        self.opt_outs = OptOutResource(self._http)
        self.smart_links = SmartLinkResource(self._http)

    def close(self) -> None:
        """Close the internal synchronous HTTP client."""
        self._http.close()

    async def aclose(self) -> None:
        """Close the internal asynchronous HTTP client."""
        await self._http.aclose()

    def __enter__(self) -> "AraraClient":
        """Enter the synchronous context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the synchronous context manager."""
        self.close()

    async def __aenter__(self) -> "AraraClient":
        """Enter the asynchronous context manager."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the asynchronous context manager."""
        await self.aclose()
