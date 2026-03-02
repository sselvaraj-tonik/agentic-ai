from typing import Dict, Optional
from pydantic import BaseModel, Field

# Input schema for get_customer_profile tool
class GetCustomerProfileInput(BaseModel):
    mobileno: str = Field(..., description="The mobile number of the customer (e.g., '631234567890').")

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
