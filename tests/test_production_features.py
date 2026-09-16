import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import settings
from app.core.security import mask_pii

def test_multi_env():
    print(f"Current Environment: {settings.APP_ENV}")
    print(f"App Name: {settings.APP_NAME}")
    print(f"LLM Provider: {settings.LLM_PROVIDER}")
    print(f"Persistence: {settings.PERSISTENCE_TYPE}")

def test_pii_masking():
    test_cases = [
        "My email is test@example.com and my phone is 09123456789.",
        "Transfer money to account 123456789012.",
        "My card number is 1234-5678-9012-3456."
    ]

    # Enable masking temporarily for test
    settings.ENABLE_PII_MASKING = True
    print("\nPII Masking Test (Enabled):")
    for case in test_cases:
        print(f"Original: {case}")
        print(f"Masked:   {mask_pii(case)}")

    settings.ENABLE_PII_MASKING = False
    print("\nPII Masking Test (Disabled):")
    for case in test_cases:
        print(f"Original: {case}")
        print(f"Masked:   {mask_pii(case)}")

if __name__ == "__main__":
    test_multi_env()
    test_pii_masking()
