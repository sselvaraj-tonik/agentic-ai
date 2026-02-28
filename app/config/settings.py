from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application Settings using Pydantic Settings.
    Reads from environment variables and .env file.
    """
    # LLM Configuration
    OLLAMA_MODEL: str = "llama3.1"
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"

    # API Configuration
    BANK_API_URL: str = "https://test.alb.tonikbank.com/customer/v1/profileinfo"
    API_TIMEOUT: int = 10

    # Application Configuration
    APP_NAME: str = "Banking Agent AI"
    APP_VERSION: str = "1.2.0"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Allow extra fields in .env
    )

settings = Settings()
