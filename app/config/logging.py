import logging
import sys
from app.config.settings import settings
from app.core.security import mask_pii

class PIIMaskingFormatter(logging.Formatter):
    """
    Custom formatter that masks PII in log messages.
    """
    def format(self, record):
        original_msg = super().format(record)
        return mask_pii(original_msg)

def setup_logging():
    """
    Configures logging for the application.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    handler = logging.StreamHandler(sys.stdout)
    formatter = PIIMaskingFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    root_logger.addHandler(handler)

    # Suppress overly verbose logs from libraries if needed
    logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(settings.APP_NAME)
