from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_BATCH_SIZE = 1000
FORBIDDEN_VARIABLE_CHARS = ("\n", "\r", "\t")


def _check_variables(values: Optional[List[str]]) -> Optional[List[str]]:
    """Reject variables with newlines or tabs, which WhatsApp refuses."""
    if not values:
        return values
    for item in values:
        if any(char in item for char in FORBIDDEN_VARIABLE_CHARS):
            raise ValueError("Variables cannot contain newlines or tabs")
    return values


class SendMessageRequest(BaseModel):
    """Request model for sending a message.

    ``receiver`` accepts ``whatsapp:+55...``, ``+55...`` or digits only; the
    API normalizes and validates it. ``media_url`` is deprecated (the API drops
    it on 2027-01-01); send header media as ``variables[0]``.
    """

    model_config = ConfigDict(populate_by_name=True)

    receiver: str
    sender: Optional[str] = None
    template_name: Optional[str] = Field(None, alias="templateName")
    template_variables: Optional[List[str]] = Field(None, alias="variables")
    smart_link_param: Optional[str] = Field(None, alias="smartLinkParam")
    smart_link_url: Optional[str] = Field(None, alias="smartLinkUrl")
    body: Optional[str] = None
    reply_to: Optional[str] = Field(None, alias="replyTo")
    media_url: Optional[str] = Field(None, alias="media_url")
    scheduled_at: Optional[datetime] = Field(None, alias="scheduled_at")
    mode: Optional[str] = None

    @field_validator("template_variables")
    @classmethod
    def validate_variables(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        """Reject variables with newlines or tabs."""
        return _check_variables(value)


class MessageResponse(BaseModel):
    """A message as returned by ``POST /v1/messages`` and ``GET /v1/messages/{id}``.

    ``cost`` is null in TEST mode, for scheduled messages and when pricing
    could not be computed up front.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    status: str
    mode: str
    sender: Optional[str] = None
    receiver: str
    body: Optional[str] = None
    cost: Optional[Decimal] = None
    reason: Optional[str] = None


class BatchMessageItem(BaseModel):
    """One recipient of a batch send."""

    model_config = ConfigDict(populate_by_name=True)

    receiver: str
    variables: Optional[List[str]] = None
    sender: Optional[str] = None

    @field_validator("variables")
    @classmethod
    def validate_variables(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        """Reject variables with newlines or tabs."""
        return _check_variables(value)


class BatchMessageRequest(BaseModel):
    """``POST /v1/messages/batch``: same template to up to 1000 recipients."""

    model_config = ConfigDict(populate_by_name=True)

    template_name: str = Field(..., alias="templateName")
    messages: List[BatchMessageItem] = Field(
        ..., min_length=1, max_length=MAX_BATCH_SIZE
    )


class BatchMessageItemResponse(BaseModel):
    """Per-recipient result of a batch; ``id`` and ``cost`` are null on failure."""

    id: Optional[str] = None
    receiver: str
    status: str
    cost: Optional[Decimal] = None


class BatchMessageResponse(BaseModel):
    """Result of a batch send."""

    model_config = ConfigDict(populate_by_name=True)

    batch_id: str = Field(..., alias="batchId")
    template_name: Optional[str] = Field(None, alias="templateName")
    total: int
    accepted: int
    total_cost: Optional[Decimal] = Field(None, alias="totalCost")
    messages: List[BatchMessageItemResponse] = []
