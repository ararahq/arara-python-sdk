from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CampaignContactRequest(BaseModel):
    """A campaign recipient (``to`` accepts the same formats as ``receiver``)."""

    to: str
    variables: List[str] = []


class CampaignRequest(BaseModel):
    """Request model for creating a campaign."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    template_name: str = Field(..., alias="templateName")
    sender: Optional[str] = None
    contacts: List[CampaignContactRequest]
    scheduled_at: Optional[datetime] = Field(None, alias="scheduledAt")
    ab_test: Optional[Dict[str, Any]] = Field(None, alias="abTest")


class CampaignResponse(BaseModel):
    """Response model for a created campaign."""

    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    status: str
    total_messages: int = Field(..., alias="totalMessages")
    total_cost: Decimal = Field(..., alias="totalCost")
    scheduled_at: Optional[datetime] = Field(None, alias="scheduledAt")


class CampaignListItem(BaseModel):
    """A campaign row in ``GET /v1/campaigns``."""

    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    name: str
    status: str
    template_name: str = Field(..., alias="templateName")
    total_messages: int = Field(..., alias="totalMessages")
    sent_count: int = Field(0, alias="sentCount")
    delivered_count: int = Field(0, alias="deliveredCount")
    read_count: int = Field(0, alias="readCount")
    failed_count: int = Field(0, alias="failedCount")
    total_cost: Decimal = Field(..., alias="totalCost")
    scheduled_at: Optional[datetime] = Field(None, alias="scheduledAt")
    created_at: Optional[datetime] = Field(None, alias="createdAt")


class CampaignBlockReason(BaseModel):
    """Why part of the audience was blocked, and how many contacts."""

    motivo: str
    quantidade: int


class CampaignDetailResponse(CampaignListItem):
    """``GET /v1/campaigns/{id}``: counters, refunds and timeline."""

    template_body: Optional[str] = Field(None, alias="templateBody")
    clicked_count: int = Field(0, alias="clickedCount")
    converted_count: int = Field(0, alias="convertedCount")
    converted_value: Decimal = Field(Decimal(0), alias="convertedValue")
    reply_count: int = Field(0, alias="replyCount")
    holdout_count: int = Field(0, alias="holdoutCount")
    blocked_count: int = Field(0, alias="blockedCount")
    block_reasons: List[CampaignBlockReason] = Field([], alias="blockReasons")
    refund_count: int = Field(0, alias="refundCount")
    refund_value: Decimal = Field(Decimal(0), alias="refundValue")
    started_at: Optional[datetime] = Field(None, alias="startedAt")
    finished_at: Optional[datetime] = Field(None, alias="finishedAt")


class CampaignListResponse(BaseModel):
    """``GET /v1/campaigns``: ``{content, totalPages, totalElements}``."""

    model_config = ConfigDict(populate_by_name=True)

    content: List[CampaignListItem]
    total_pages: int = Field(..., alias="totalPages")
    total_elements: int = Field(..., alias="totalElements")
