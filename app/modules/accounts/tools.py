import requests
from langchain_core.tools import tool
from app.config.settings import settings
from app.core.exceptions import APIError

@tool
def get_customer_profile(mobileno: str) -> dict:
    """
    Retrieves customer profile information based on their mobile number.

    Args:
        mobileno (str): The mobile number of the customer (e.g., "631234567890").

    Returns:
        dict: The customer profile data or an error message.
    """
    params = {"mobileno": mobileno}

    try:
        response = requests.get(
            settings.BANK_API_URL,
            params=params,
            timeout=settings.API_TIMEOUT
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
