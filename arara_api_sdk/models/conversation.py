from uuid import UUID

from pydantic import BaseModel, Field


class ConversationReplyRequest(BaseModel):
    """Request model for replying inside an open conversation window."""
    conversation_id: UUID = Field(..., alias="conversationId")
    body: str

    class Config:
        populate_by_name = True
