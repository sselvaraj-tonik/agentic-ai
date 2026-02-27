from typing import List, Optional
from pydantic import BaseModel

class Payee(BaseModel):
    name: str
    payee_id: str
    bank: str

class TransferRequest(BaseModel):
    payee_id: str
    amount: float
    currency: str = "PHP"
