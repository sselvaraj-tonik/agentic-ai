from langchain_core.tools import tool
from typing import List, Dict
from app.modules.common.schemas import SearchPayeeInput, ExecuteTransferInput

# Mock payee data
PAYEES = {
    "xavier": [
        {"payee_id": "P_001", "name": "Xavier ABC", "bank": "HDFC"},
        {"payee_id": "P_002", "name": "Xavier XYZ", "bank": "SBI"}
    ]
}

@tool(args_schema=SearchPayeeInput)
def search_payee(name: str) -> dict:
    """
    YOU MUST CALL THIS TOOL FIRST whenever the user wants to send money or transfer funds to a person by name.
    Searches for a payee by name to get their exact payee_id and bank details.
    """
    name_lower = name.lower()
    for key in PAYEES:
        if key in name_lower:
            return {"results": PAYEES[key]}
    return {"results": []}

@tool(args_schema=ExecuteTransferInput)
def execute_transfer(payee_id: str, amount: float) -> dict:
    """Executes a money transfer. ALWAYS get user confirmation before calling this."""
    return {"status": "SUCCESS", "transaction_id": "TXN_998877", "amount_sent": amount, "to_payee": payee_id}
