from pydantic import BaseModel, Field
from datetime import date

# Input schemas for tools
class CheckLoanStatusInput(BaseModel):
    account_id: str = Field(..., description="The ID of the account to check the loan status for.")

class ProcessLoanPaymentInput(BaseModel):
    loan_id: str = Field(..., description="The ID of the loan to make a payment towards.")
    amount: float = Field(..., description="The amount to pay.")

# Return schemas
class LoanStatus(BaseModel):
    loan_id: str
    emi_status: str
    emi_amount: float
    due_date: date
