from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM Configuration
    OLLAMA_MODEL: str
    OLLAMA_BASE_URL: str

    # API Configuration
    BANK_API_BASE_URL: str
    DRUPAL_FAQ_URL: str
    API_TIMEOUT: int = 10

    # Database Configuration
    DATABASE_URL: str

    # Application Configuration
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()