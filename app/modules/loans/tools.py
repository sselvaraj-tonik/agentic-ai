from langchain_core.tools import tool
from app.modules.loans.schemas import CheckLoanStatusInput, ProcessLoanPaymentInput

@tool(args_schema=CheckLoanStatusInput)
def check_loan_status(account_id: str) -> dict:
    """Checks if the user has a pending Loan EMI for this month."""
    return {
        "loan_id": "L_5544",
        "emi_status": "PENDING",
        "emi_amount": 15000.00,
        "due_date": "2026-03-05"
    }

@tool(args_schema=ProcessLoanPaymentInput)
def process_loan_payment(loan_id: str, amount: float) -> dict:
    """Processes the payment for a loan EMI. ALWAYS get user confirmation first."""
    return {"status": "SUCCESS", "message": f"EMI of {amount} paid successfully for loan {loan_id}."}
