from arara_api_sdk.resources import BaseResource
from arara_api_sdk.models.wallet import (
    AutoRechargeSettingsDTO,
    UpdateAutoRechargeRequest,
    WalletTransactionPageDTO,
)


class WalletResource(BaseResource):
    """Resource for wallet transactions and auto-recharge settings."""

    def transactions(self, page: int = 0, size: int = 20) -> WalletTransactionPageDTO:
        """GET /v1/wallet/transactions — ledger page synchronously."""
        return self._http.request(
            "GET", "/v1/wallet/transactions",
            response_model=WalletTransactionPageDTO,
            params={"page": page, "size": size},
        )

    async def transactions_async(
        self, page: int = 0, size: int = 20
    ) -> WalletTransactionPageDTO:
        """GET /v1/wallet/transactions — ledger page asynchronously."""
        return await self._http.arequest(
            "GET", "/v1/wallet/transactions",
            response_model=WalletTransactionPageDTO,
            params={"page": page, "size": size},
        )

    def get_auto_recharge(self) -> AutoRechargeSettingsDTO:
        """GET /v1/wallet/auto-recharge — settings synchronously."""
        return self._http.request(
            "GET", "/v1/wallet/auto-recharge",
            response_model=AutoRechargeSettingsDTO,
        )

    async def get_auto_recharge_async(self) -> AutoRechargeSettingsDTO:
        """GET /v1/wallet/auto-recharge — settings asynchronously."""
        return await self._http.arequest(
            "GET", "/v1/wallet/auto-recharge",
            response_model=AutoRechargeSettingsDTO,
        )

    def update_auto_recharge(
        self, request: UpdateAutoRechargeRequest
    ) -> AutoRechargeSettingsDTO:
        """PATCH /v1/wallet/auto-recharge — updates settings synchronously."""
        return self._http.request(
            "PATCH", "/v1/wallet/auto-recharge",
            response_model=AutoRechargeSettingsDTO,
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

    async def update_auto_recharge_async(
        self, request: UpdateAutoRechargeRequest
    ) -> AutoRechargeSettingsDTO:
        """PATCH /v1/wallet/auto-recharge — updates settings asynchronously."""
        return await self._http.arequest(
            "PATCH", "/v1/wallet/auto-recharge",
            response_model=AutoRechargeSettingsDTO,
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
