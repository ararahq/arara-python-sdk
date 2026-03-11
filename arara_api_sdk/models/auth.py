from typing import Optional
from pydantic import BaseModel, EmailStr

class UserResponseDTO(BaseModel):
    """Data Transfer Object for User response."""
    name: str
    email: EmailStr
    role: Optional[str] = None
