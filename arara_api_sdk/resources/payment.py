from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from arara_api_sdk.resources import BaseResource
from arara_api_sdk.models.payment import (
    AbacatePayPixRequest, 
    AbacatePayPixResponse,
    CreatePaymentRequest
)

class PaymentResource(BaseResource):
    """Resource for managing payments and credits."""

    def create_pix(self, request: AbacatePayPixRequest) -> AbacatePayPixResponse:
        """Creates a Pix payment via AbacatePay synchronously.

        Args:
            request: The payment details.

        Returns:
            The created Pix payment response including QR code/Copy-Paste.
        """
        return self._http.request(
            "POST", "/payments/pix", 
            response_model=AbacatePayPixResponse,
            json=request.model_dump(by_alias=True, exclude_none=True)
        )

    async def create_pix_async(self, request: AbacatePayPixRequest) -> AbacatePayPixResponse:
        """Creates a Pix payment via AbacatePay asynchronously.

        Args:
            request: The payment details.

        Returns:
            The created Pix payment response including QR code/Copy-Paste.
        """
        return await self._http.arequest(
            "POST", "/payments/pix", 
            response_model=AbacatePayPixResponse,
            json=request.model_dump(by_alias=True, exclude_none=True)
        )

    def checkout(self, request: CreatePaymentRequest) -> Any:
        """Creates a checkout session for credits synchronously.

        Args:
            request: Checkout session parameters.

        Returns:
            The checkout session response.
        """
        return self._http.request(
            "POST", "/payments/checkout", 
            json=request.model_dump(exclude_none=True)
        )

    async def checkout_async(self, request: CreatePaymentRequest) -> Any:
        """Creates a checkout session for credits asynchronously.

        Args:
            request: Checkout session parameters.

        Returns:
            The checkout session response.
        """
        return await self._http.arequest(
            "POST", "/payments/checkout", 
            json=request.model_dump(exclude_none=True)
        )
