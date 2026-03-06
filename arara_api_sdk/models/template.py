from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class TemplateResponse(BaseModel):
    """Response model for a Template."""
    id: UUID
    name: str
    formatted_name: str = Field(..., alias="formattedName")
    category: str
    original_category: Optional[str] = Field(None, alias="originalCategory")
    language: str
    provider_name: str = Field(..., alias="providerName")
    provider_template_id: str = Field(..., alias="providerTemplateId")
    provider_status: str = Field(..., alias="providerStatus")
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")
    body_preview: Optional[str] = Field(None, alias="bodyPreview")
    structure_json: Dict[str, Any] = Field(..., alias="structureJson")
    usage_guide: Optional[Dict[str, Any]] = Field(None, alias="usageGuide")
    variables_schema: Optional[Dict[str, str]] = Field(None, alias="variablesSchema")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        populate_by_name = True

class CreateTemplateRequest(BaseModel):
    """Request model for creating a new Template."""
    name: str
    category: str
    language: str
    structure_json: Dict[str, Any] = Field(..., alias="structureJson")

    class Config:
        populate_by_name = True

class TemplateStatusResponse(BaseModel):
    """Response for template status checking."""
    status: str
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")
    category: str

    class Config:
        populate_by_name = True
