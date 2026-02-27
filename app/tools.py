import os
import requests
from langchain_core.tools import tool

@tool
def get_customer_profile(mobileno: str) -> dict:
    """
    Retrieves customer profile information based on their mobile number.

    Args:
        mobileno (str): The mobile number of the customer (e.g., "631234567890").

    Returns:
        dict: The customer profile data or an error message.
    """
    # Base URL from env var or default
    base_url = os.getenv("BANK_API_URL", "https://test.alb.tonikbank.com/customer/v1/profileinfo")

    # Construct query parameters
    params = {"mobileno": mobileno}

    try:
        # Perform the GET request
        # Adding a timeout for production readiness
        response = requests.get(base_url, params=params, timeout=10)

        # Raise an exception for HTTP errors (4xx, 5xx)
        response.raise_for_status()

        # Return the JSON content
        return response.json()

    except requests.exceptions.RequestException as e:
        # Return a structured error so the agent can handle it gracefully
        return {"error": f"API request failed: {str(e)}"}

@tool
def search_payee(name: str) -> dict:
    """
    YOU MUST CALL THIS TOOL FIRST whenever the user wants to send money or transfer funds to a person by name. 
    Searches for a payee by name to get their exact payee_id and bank details.
    """
    name = name.lower()
    if "xavier" in name:
        return {
            "results": [
                {"payee_id": "P_001", "name": "Xavier ABC", "bank": "HDFC"},
                {"payee_id": "P_002", "name": "Xavier XYZ", "bank": "SBI"}
            ]
        }
    return {"results": []}

@tool
def execute_transfer(payee_id: str, amount: float) -> dict:
    """Executes a money transfer. ALWAYS get user confirmation before calling this."""
    return {"status": "SUCCESS", "transaction_id": "TXN_998877", "amount_sent": amount, "to_payee": payee_id}

@tool
def check_loan_status(account_id: str) -> dict:
    """Checks if the user has a pending Loan EMI for this month."""
    return {
        "loan_id": "L_5544",
        "emi_status": "PENDING",
        "emi_amount": 15000.00,
        "due_date": "2026-03-05"
    }

@tool
def process_loan_payment(loan_id: str, amount: float) -> dict:
    """Processes the payment for a loan EMI. ALWAYS get user confirmation first."""
    return {"status": "SUCCESS", "message": f"EMI of {amount} paid successfully for loan {loan_id}."}