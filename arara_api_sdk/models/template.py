from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_TEMPLATE_LANGUAGE = "pt_BR"


class TemplateResponse(BaseModel):
    """Response model for a Template."""

    model_config = ConfigDict(populate_by_name=True)

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
    available_for_sending: bool = Field(True, alias="availableForSending")
    unavailable_reason: Optional[str] = Field(None, alias="unavailableReason")
    body_preview: Optional[str] = Field(None, alias="bodyPreview")
    structure_json: Any = Field(None, alias="structureJson")
    usage_guide: Optional[Dict[str, Any]] = Field(None, alias="usageGuide")
    variables_schema: Optional[Dict[str, str]] = Field(None, alias="variablesSchema")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")


class TemplateButton(BaseModel):
    """A template button (``QUICK_REPLY``, ``URL``, ``PHONE_NUMBER``, ...)."""

    model_config = ConfigDict(populate_by_name=True)

    type: str
    text: str
    url: Optional[str] = None
    phone: Optional[str] = None
    extra_config: Optional[Dict[str, Any]] = Field(None, alias="extraConfig")
    flow_id: Optional[UUID] = Field(None, alias="flowId")


class CarouselCard(BaseModel):
    """A carousel card: media, body and up to two buttons."""

    model_config = ConfigDict(populate_by_name=True)

    media_url: str = Field(..., alias="mediaUrl")
    body: str
    buttons: Optional[List[TemplateButton]] = None


class CreateTemplateRequest(BaseModel):
    """Request model for ``POST /v1/templates``.

    ``body`` is required; ``samples`` maps each body variable (``"1"``,
    ``"2"``...) to an example value for Meta review.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    category: str
    body: str
    language: str = DEFAULT_TEMPLATE_LANGUAGE
    header: Optional[str] = None
    header_type: Optional[str] = Field(None, alias="headerType")
    footer: Optional[str] = None
    buttons: Optional[List[TemplateButton]] = None
    samples: Optional[Dict[str, str]] = None
    variable_examples: Optional[List[str]] = Field(None, alias="variableExamples")
    carousel_cards: Optional[List[CarouselCard]] = Field(None, alias="carouselCards")


class TemplateStatusResponse(BaseModel):
    """Response for template status checking."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    status: str
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")
    category: Optional[str] = None
