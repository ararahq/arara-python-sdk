from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CurrentUserResponse(BaseModel):
    """``GET /auth/me``: the user that owns the API key.

    Only the stable fields are typed; anything else the API returns is kept
    as extra attributes.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    organization_id: Optional[str] = Field(None, alias="organizationId")
