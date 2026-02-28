class BankingAgentException(Exception):
    """Base exception for the banking agent application."""
    pass

class APIError(BankingAgentException):
    """Exception raised when an external API call fails."""
    pass

class LLMError(BankingAgentException):
    """Exception raised when the LLM service fails."""
    pass
