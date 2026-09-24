from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CurrentUserResponse(BaseModel):
    """``GET /auth/me``: the user that owns the API key.

    Mirrors ``UserResponseDTO {name, email, role, emailPending}``; unknown
    fields the API may add later are kept as extra attributes.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    name: str
    email: str
    role: Optional[str] = None
    email_pending: bool = Field(False, alias="emailPending")
