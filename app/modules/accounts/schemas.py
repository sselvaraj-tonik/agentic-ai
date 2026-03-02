from typing import Dict, Optional
from pydantic import BaseModel, Field

# Input schema for get_customer_profile tool
class GetCustomerProfileInput(BaseModel):
    mobileno: str = Field(..., description="The mobile number of the customer (e.g., '631234567890').")

class SearchPayeeInput(BaseModel):
    name: str = Field(..., description="The name of the payee to search for.")

class ExecuteTransferInput(BaseModel):
    payee_id: str = Field(..., description="The exact ID of the payee to send money to.")
    amount: float = Field(..., description="The amount of money to transfer.")

# Return schemas (optional, good for consistency)
class CustomerProfile(BaseModel):
    name: str
    account_id: str
    mobile: str
    status: str
    balance: float

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
