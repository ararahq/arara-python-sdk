from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from uuid import UUID

class OrganizationBrainConfig(BaseModel):
    """Configuration for Organization's AI Brain."""
    can_use_ai: bool = Field(..., alias="canUseAi")
    is_ai_agent_enabled: bool = Field(..., alias="isAiAgentEnabled")

    class Config:
        populate_by_name = True

class UpdateBrainConfigRequest(BaseModel):
    """Request to update UI Brain configuration."""
    is_ai_agent_enabled: Optional[bool] = Field(None, alias="isAiAgentEnabled")

    class Config:
        populate_by_name = True

class WebhookConfig(BaseModel):
    """Webhook configuration for an organization."""
    url: str
    secret: str
    is_shared_number: bool = Field(..., alias="isSharedNumber")

    class Config:
        populate_by_name = True

class UpdateWebhookRequest(BaseModel):
    """Request to update webhook configuration."""
    url: Optional[str] = None
    secret: Optional[str] = None

class InviteUserRequest(BaseModel):
    """Request to invite a new user to the organization."""
    email: str

class InvitationResponse(BaseModel):
    """Response after inviting a user."""
    message: str
    token: str

class OrganizationNumber(BaseModel):
    """Model for an organization's phone number."""
    id: str
    name: str
    phone_number: str = Field(..., alias="phoneNumber")
    type: str
    is_default: bool = Field(..., alias="isDefault")
    alias: str

    class Config:
        populate_by_name = True

class UpdateNumberRequest(BaseModel):
    """Request to update a phone number's details."""
    alias: Optional[str] = None
    is_default: Optional[bool] = Field(None, alias="isDefault")

    class Config:
        populate_by_name = True
