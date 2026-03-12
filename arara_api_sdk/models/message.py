from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from decimal import Decimal

class SendMessageRequest(BaseModel):
    """Request model for sending a message."""
    receiver: str
    sender: Optional[str] = None
    template_name: Optional[str] = Field(None, alias="templateName")
    template_variables: Optional[List[str]] = Field(None, alias="variables")
    smart_link_param: Optional[str] = Field(None, alias="smartLinkParam")
    smart_link_url: Optional[str] = Field(None, alias="smartLinkUrl")
    body: Optional[str] = None
    media_url: Optional[str] = Field(None, alias="media_url")  # Deprecated: use variables[0] for header media
    scheduled_at: Optional[datetime] = Field(None, alias="scheduled_at")
    mode: Optional[str] = None  # LIVE or TEST

    class Config:
        populate_by_name = True

    @field_validator("template_variables")
    @classmethod
    def validate_variables(cls, v):
        if v:
            for item in v:
                if any(c in item for c in ["\n", "\r", "\t"]):
                    raise ValueError("Variables cannot contain newlines or tabs")
        return v

class MessageResponse(BaseModel):
    """Response model for a sent message."""
    id: str
    status: str
    mode: str
    sender: Optional[str] = None
    receiver: str
    body: Optional[str] = None
    cost: Decimal

    class Config:
        populate_by_name = True
