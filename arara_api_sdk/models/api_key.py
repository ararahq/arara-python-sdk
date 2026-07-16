from typing import Optional

from pydantic import BaseModel, Field


class ApiKey(BaseModel):
    """Metadata for an existing API key (never exposes the secret)."""
    id: str
    name: Optional[str] = None
    prefix: str
    last_four: Optional[str] = Field(None, alias="lastFour")
    mode: str
    scope: Optional[str] = None
    created_at: Optional[str] = Field(None, alias="createdAt")
    last_used_at: Optional[str] = Field(None, alias="lastUsedAt")
    expires_at: Optional[str] = Field(None, alias="expiresAt")
    expired: Optional[bool] = None
    ip_allowlist: Optional[str] = Field(None, alias="ipAllowlist")
    rotated_from_id: Optional[str] = Field(None, alias="rotatedFromId")

    class Config:
        populate_by_name = True


class GeneratedApiKey(BaseModel):
    """A freshly created API key, including the one-time plaintext secret."""
    plain_text_key: str = Field(..., alias="plainTextKey")
    prefix: Optional[str] = None
    last_four_chars: Optional[str] = Field(None, alias="lastFourChars")
    mode: Optional[str] = None
    created_at: Optional[str] = Field(None, alias="createdAt")

    class Config:
        populate_by_name = True
