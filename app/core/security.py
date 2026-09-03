import re
from app.config.settings import settings

# Regular expressions for common PII
PII_PATTERNS = [
    ("email", r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    ("card_number", r"\b(?:\d[ -]*?){13,16}\b"),
    ("account_number", r"\b\d{12,16}\b"),
    ("phone", r"\b\d{10,11}\b"),
]

def mask_pii(text: str) -> str:
    """
    Redacts PII from the given text if PII masking is enabled.
    """
    if not settings.ENABLE_PII_MASKING:
        return text

    masked_text = text
    for pii_type, pattern in PII_PATTERNS:
        masked_text = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", masked_text)

    return masked_text
