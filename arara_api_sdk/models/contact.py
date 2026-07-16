from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ContactRequest(BaseModel):
    """Request model for importing a contact."""
    name: str
    phone: str
    email: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


class ContactPatchRequest(BaseModel):
    """Request model for updating a contact."""
    name: Optional[str] = None
    email: Optional[str] = None
    tags: Optional[List[str]] = None


class ContactResponse(BaseModel):
    """Response model for a single contact."""
    id: UUID
    name: str
    phone: str
    email: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    created_at: str = Field(..., alias="createdAt")
    lifecycle: str
    source: str
    outbound_count: int = Field(..., alias="outboundCount")
    inbound_count: int = Field(..., alias="inboundCount")
    first_seen_at: Optional[str] = Field(None, alias="firstSeenAt")
    last_outbound_at: Optional[str] = Field(None, alias="lastOutboundAt")
    last_inbound_at: Optional[str] = Field(None, alias="lastInboundAt")
    last_message_at: Optional[str] = Field(None, alias="lastMessageAt")
    opt_out_at: Optional[str] = Field(None, alias="optOutAt")
    last_template_name: Optional[str] = Field(None, alias="lastTemplateName")

    class Config:
        populate_by_name = True


class ContactsListResponse(BaseModel):
    """Paginated list of contacts."""
    contacts: List[ContactResponse]
    total: int
    page: int
    size: int
    total_pages: int = Field(..., alias="totalPages")

    class Config:
        populate_by_name = True


class ContactsBatchError(BaseModel):
    """A single failed row in a batch import."""
    index: int
    phone: Optional[str] = None
    reason: str


class ContactsBatchResponse(BaseModel):
    """Result of a batch contact import."""
    import_id: UUID = Field(..., alias="importId")
    created: int
    updated: int
    skipped: int
    errors: List[ContactsBatchError] = []

    class Config:
        populate_by_name = True


class ContactsStatsResponse(BaseModel):
    """Aggregate lifecycle counts for the organization's contacts."""
    total: int
    new_count: int = Field(..., alias="newCount")
    engaged: int
    silent: int
    dormant: int
    opted_out: int = Field(..., alias="optedOut")

    class Config:
        populate_by_name = True


class ContactsReactivationCandidate(BaseModel):
    """A dormant contact eligible for reactivation."""
    phone: str
    name: str
    last_message_at: Optional[str] = Field(None, alias="lastMessageAt")
    last_template_name: Optional[str] = Field(None, alias="lastTemplateName")

    class Config:
        populate_by_name = True


class ContactsReactivationResponse(BaseModel):
    """List of reactivation candidates."""
    total: int
    candidates: List[ContactsReactivationCandidate]


class ContactMessageItem(BaseModel):
    """A single message in a contact's history."""
    id: UUID
    direction: str
    status: str
    template_name: Optional[str] = Field(None, alias="templateName")
    body: Optional[str] = None
    created_at: str = Field(..., alias="createdAt")

    class Config:
        populate_by_name = True


class ContactMessagesResponse(BaseModel):
    """Message history for a contact."""
    phone: str
    total: int
    messages: List[ContactMessageItem]
