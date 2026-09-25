from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class WalletTransactionDTO(BaseModel):
    """A single wallet ledger entry."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    amount: Decimal
    type: str
    description: Optional[str] = None
    reference_id: Optional[str] = Field(None, alias="referenceId")
    mode: str
    created_at: Optional[datetime] = Field(None, alias="createdAt")


class WalletTransactionPageDTO(BaseModel):
    """Paginated wallet transactions."""

    model_config = ConfigDict(populate_by_name=True)

    content: List[WalletTransactionDTO]
    page: int
    size: int
    total_elements: int = Field(..., alias="totalElements")
    total_pages: int = Field(..., alias="totalPages")


class AutoRechargeSettingsDTO(BaseModel):
    """Auto-recharge configuration for the organization's wallet."""

    model_config = ConfigDict(populate_by_name=True)

    enabled: bool
    threshold: Decimal
    amount: Decimal
    last_attempt_at: Optional[datetime] = Field(None, alias="lastAttemptAt")
    last_failure_reason: Optional[str] = Field(None, alias="lastFailureReason")


class UpdateAutoRechargeRequest(BaseModel):
    """Request to update auto-recharge settings."""

    enabled: Optional[bool] = None
    threshold: Optional[Decimal] = None
    amount: Optional[Decimal] = None
