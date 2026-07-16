from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class NumberCardDTO(BaseModel):
    """Detailed card for a single phone number, including health metrics."""
    id: str
    name: str
    alias: Optional[str] = None
    description: Optional[str] = None
    phone_number: str = Field(..., alias="phoneNumber")
    type: str
    is_default: bool = Field(..., alias="isDefault")
    status: str
    quality_score: str = Field(..., alias="qualityScore")
    messaging_tier: str = Field(..., alias="messagingTier")
    verified_at: Optional[datetime] = Field(None, alias="verifiedAt")
    last_health_check_at: Optional[datetime] = Field(None, alias="lastHealthCheckAt")
    provider: str
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    messages_last_7d: int = Field(..., alias="messagesLast7d")
    messages_last_30d: int = Field(..., alias="messagesLast30d")

    class Config:
        populate_by_name = True


class NumbersSlotDTO(BaseModel):
    """Plan slot info for dedicated numbers."""
    used: int
    max: int
    plan_label: str = Field(..., alias="planLabel")
    at_cap: bool = Field(..., alias="atCap")
    no_entitlement: bool = Field(..., alias="noEntitlement")
    monthly_price_cents: int = Field(..., alias="monthlyPriceCents")
    monthly_total_cents: int = Field(..., alias="monthlyTotalCents")

    class Config:
        populate_by_name = True


class NumbersResponseDTO(BaseModel):
    """Numbers list with plan slot info."""
    numbers: List[NumberCardDTO]
    slot: NumbersSlotDTO


class RequestNumberRequest(BaseModel):
    """Request a new dedicated number."""
    reason: Optional[str] = None
    expected_volume: Optional[str] = Field(None, alias="expectedVolume")
    area_code: Optional[str] = Field(None, alias="areaCode")
    display_name: Optional[str] = Field(None, alias="displayName")
    profile_picture_url: Optional[str] = Field(None, alias="profilePictureUrl")

    class Config:
        populate_by_name = True


class UpdateNumberRequest(BaseModel):
    """Update a phone number's editable fields."""
    alias: Optional[str] = None
    is_default: Optional[bool] = Field(None, alias="isDefault")
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        populate_by_name = True
