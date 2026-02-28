from typing import Optional
from pydantic import BaseModel
from datetime import date

class LoanStatus(BaseModel):
    loan_id: str
    emi_status: str
    emi_amount: float
    due_date: date
