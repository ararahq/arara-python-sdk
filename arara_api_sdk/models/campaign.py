from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal

class CampaignContactRequest(BaseModel):
    """Request model for a contact in a campaign."""
    to: str
    variables: List[str] = []

class CampaignRequest(BaseModel):
    """Request model for creating a campaign."""
    name: str
    template_name: str = Field(..., alias="templateName")
    sender: Optional[str] = None
    contacts: List[CampaignContactRequest]

    class Config:
        populate_by_name = True

class CampaignResponse(BaseModel):
    """Response model for a campaign."""
    id: UUID
    name: str
    status: str
    total_messages: int = Field(..., alias="totalMessages")
    total_cost: Decimal = Field(..., alias="totalCost")

    class Config:
        populate_by_name = True
