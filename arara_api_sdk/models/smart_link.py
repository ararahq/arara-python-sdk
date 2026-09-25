from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateWhatsAppSmartLinkRequest(BaseModel):
    """Request to create a WhatsApp smart link."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    phone_number: str = Field(..., alias="phoneNumber")
    default_text: Optional[str] = Field(None, alias="defaultText")
    qr_code_color: Optional[str] = Field("BLACK", alias="qrCodeColor")


class UpdateWhatsAppSmartLinkRequest(BaseModel):
    """Request to update a WhatsApp smart link."""

    model_config = ConfigDict(populate_by_name=True)

    name: Optional[str] = None
    default_text: Optional[str] = Field(None, alias="defaultText")
    qr_code_color: Optional[str] = Field(None, alias="qrCodeColor")


class WhatsAppSmartLinkResponse(BaseModel):
    """Response model for a WhatsApp smart link."""

    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    phone_number: str = Field(..., alias="phoneNumber")
    default_text: Optional[str] = Field(None, alias="defaultText")
    qr_code_color: str = Field(..., alias="qrCodeColor")
    code: str
    short_url: str = Field(..., alias="shortUrl")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    clicks: int = 0
