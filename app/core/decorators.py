import time
import functools
from app.config.logging import logger
from app.config.settings import settings

def log_execution_time(func):
    """
    Decorator to log the execution time of a function if DEBUG is enabled.
    Also logs when the function starts and ends, helping trace the execution path.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not settings.DEBUG:
            return func(*args, **kwargs)

        func_name = func.__name__
        logger.debug(f"[START] Executing: {func_name}")

        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.debug(f"[END] {func_name} completed in {elapsed_time:.4f} seconds")

    return wrapper
