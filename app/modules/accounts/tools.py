import requests
from langchain_core.tools import tool
from app.config.settings import settings
from app.modules.accounts.schemas import GetCustomerProfileInput

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
