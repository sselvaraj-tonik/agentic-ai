import requests
from langchain_core.tools import tool
from typing import List, Dict
from app.config.settings import settings
from app.modules.accounts.schemas import GetCustomerProfileInput, SearchPayeeInput, ExecuteTransferInput

@tool(args_schema=GetCustomerProfileInput)
def get_customer_profile(mobileno: str) -> dict:
    """
    Retrieves customer profile information based on their mobile number.
    """
    params = {"mobileno": mobileno}

    try:
        # Construct the full URL by appending the endpoint path to the base URL
        full_url = f"{settings.BANK_API_BASE_URL.rstrip('/')}/profileinfo"

        response = requests.get(
            full_url,
            params=params,
            timeout=settings.API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

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
