from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ConversationReplyRequest(BaseModel):
    """Request model for replying inside an open conversation window."""

    model_config = ConfigDict(populate_by_name=True)

    conversation_id: UUID = Field(..., alias="conversationId")
    body: str
