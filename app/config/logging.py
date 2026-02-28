import logging
import sys
from app.config.settings import settings

def setup_logging():
    """
    Configures logging for the application.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Suppress overly verbose logs from libraries if needed
    logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(settings.APP_NAME)
