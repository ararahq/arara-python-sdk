from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class AbacatePayCustomerRequest(BaseModel):
    name: str
    cellphone: str
    email: str
    tax_id: str = Field(..., alias="taxId")

class AbacatePayPixRequest(BaseModel):
    amount: int  # Cents
    expires_in: Optional[int] = Field(3600, alias="expiresIn")
    description: Optional[str] = "Recarga de Créditos - Arara"
    customer: Optional[AbacatePayCustomerRequest] = None
    metadata: Optional[Dict[str, str]] = None

    class Config:
        populate_by_name = True

class AbacatePayPixData(BaseModel):
    id: str
    amount: int
    status: str
    br_code: str = Field(..., alias="brCode")
    br_code_base64: str = Field(..., alias="brCodeBase64")
    expires_at: str = Field(..., alias="expiresAt")

    class Config:
        populate_by_name = True

class AbacatePayPixResponse(BaseModel):
    data: AbacatePayPixData
    error: Optional[str] = None

class CreatePaymentRequest(BaseModel):
    amount: int
    method: str = "PIX"
