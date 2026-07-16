from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CreateWhatsAppSmartLinkRequest(BaseModel):
    """Request to create a WhatsApp smart link."""
    name: str
    phone_number: str = Field(..., alias="phoneNumber")
    default_text: Optional[str] = Field(None, alias="defaultText")
    qr_code_color: Optional[str] = Field("BLACK", alias="qrCodeColor")

    class Config:
        populate_by_name = True


class UpdateWhatsAppSmartLinkRequest(BaseModel):
    """Request to update a WhatsApp smart link."""
    name: Optional[str] = None
    default_text: Optional[str] = Field(None, alias="defaultText")
    qr_code_color: Optional[str] = Field(None, alias="qrCodeColor")

    class Config:
        populate_by_name = True


class WhatsAppSmartLinkResponse(BaseModel):
    """Response model for a WhatsApp smart link."""
    id: UUID
    name: str
    phone_number: str = Field(..., alias="phoneNumber")
    default_text: Optional[str] = Field(None, alias="defaultText")
    qr_code_color: str = Field(..., alias="qrCodeColor")
    code: str
    short_url: str = Field(..., alias="shortUrl")
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    clicks: int = 0

    class Config:
        populate_by_name = True
