from typing import Optional
from pydantic import BaseModel, Field

class UserUpdate(BaseModel):
    """Request model for updating user information."""
    name: Optional[str] = None
    phone_number: Optional[str] = Field(None, alias="phoneNumber")

    class Config:
        populate_by_name = True

class UserProfileResponse(BaseModel):
    """Response model for the current user profile."""
    name: str
    email: str
    phone_number: str = Field(..., alias="phoneNumber")
    document_number: str = Field(..., alias="documentNumber")
    role: str
    needs_initial_onboarding: bool = Field(..., alias="needsInitialOnboarding")

    class Config:
        populate_by_name = True
