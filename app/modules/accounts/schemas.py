from typing import Dict, Optional, List
from pydantic import BaseModel

class CustomerProfile(BaseModel):
    name: str
    account_id: str
    mobile: str
    status: str
    balance: float
    # Add other fields based on the API response structure

class AccountResponse(BaseModel):
    profile: Optional[CustomerProfile] = None
    error: Optional[str] = None

class Payee(BaseModel):
    name: str
    payee_id: str
    bank: str

class TransferRequest(BaseModel):
    payee_id: str
    amount: float
    currency: str = "PHP"
