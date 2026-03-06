from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class BrainRequest(BaseModel):
    """Request to interact with the AI Brain."""
    prompt: str
    context_type: Optional[str] = Field("HYBRID", alias="contextType")

    class Config:
        populate_by_name = True

class BrainAction(BaseModel):
    """Action suggested by the AI Brain."""
    type: str # CREATE_TEMPLATE, SCHEDULE_CAMPAIGN, etc.
    payload: Dict[str, Any]
    requires_approval: bool = Field(True, alias="requiresApproval")
    description: str

    class Config:
        populate_by_name = True

class BrainResponse(BaseModel):
    """Response from the AI Brain."""
    text: str
    suggested_action: Optional[BrainAction] = Field(None, alias="suggestedAction")

    class Config:
        populate_by_name = True
