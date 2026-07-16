from typing import Any, Optional
from arara_api_sdk.config import SDKConfig
from arara_api_sdk.http.client import HttpClient
from arara_api_sdk.resources.message import MessageResource
from arara_api_sdk.resources.template import TemplateResource
from arara_api_sdk.resources.organization import OrganizationResource
from arara_api_sdk.resources.user import UserResource
from arara_api_sdk.resources.brain import BrainResource
from arara_api_sdk.resources.campaign import CampaignResource
from arara_api_sdk.resources.payment import PaymentResource
from arara_api_sdk.resources.contact import ContactResource
from arara_api_sdk.resources.conversation import ConversationResource
from arara_api_sdk.resources.wallet import WalletResource
from arara_api_sdk.resources.number import NumberResource
from arara_api_sdk.resources.smart_link import SmartLinkResource
from arara_api_sdk.resources.api_key import ApiKeyResource

class AraraClient:
    """
    Official Arara Python SDK Client.
    
    Provides access to messages, templates, organizations, users, and AI brain features.
    Supports both synchronous and asynchronous operations.
    """

    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None
    ) -> None:
        """Initializes the Arara SDK Client.

        Args:
            api_key: The Arara API Key. If not provided, will look for the 
                ARARA_API_KEY environment variable.
            base_url: The base URL for the Arara API. Defaults to
                https://api.ararahq.com.
            timeout: Request timeout in seconds. Defaults to 30.0.
            max_retries: Maximum number of request retries. Defaults to 3.
        """
        # Allow passing config directly or via env/defaults
        config_kwargs = {}
        if api_key: config_kwargs["api_key"] = api_key
        if base_url: config_kwargs["base_url"] = base_url
        if timeout: config_kwargs["timeout"] = timeout
        if max_retries: config_kwargs["max_retries"] = max_retries
        
        self.config = SDKConfig(**config_kwargs)
        self._http = HttpClient(self.config)
        
        # Initialize resources
        self.messages = MessageResource(self._http)
        self.templates = TemplateResource(self._http)
        self.organizations = OrganizationResource(self._http)
        self.users = UserResource(self._http)
        self.brain = BrainResource(self._http)
        self.campaigns = CampaignResource(self._http)
        self.payments = PaymentResource(self._http)
        self.contacts = ContactResource(self._http)
        self.conversations = ConversationResource(self._http)
        self.wallet = WalletResource(self._http)
        self.numbers = NumberResource(self._http)
        self.smart_links = SmartLinkResource(self._http)
        self.api_keys = ApiKeyResource(self._http)

    def close(self) -> None:
        """Closes the internal synchronous HTTP client."""
        self._http.close()

    async def aclose(self) -> None:
        """Closes the internal asynchronous HTTP client."""
        await self._http.aclose()

    def __enter__(self) -> "AraraClient":
        """Context manager entry point for synchronous use."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit point for synchronous use."""
        self.close()

    async def __aenter__(self) -> "AraraClient":
        """Context manager entry point for asynchronous use."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit point for asynchronous use."""
        await self.aclose()
