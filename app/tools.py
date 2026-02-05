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
    base_url = os.getenv("BANK_API_URL", "https://bank.com/customer/v1/profileinfo")

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
