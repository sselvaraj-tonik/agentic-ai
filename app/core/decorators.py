import time
import functools
from app.config.logging import logger

def log_execution_time(func):
    """
    Decorator that logs the execution time of a function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Function '{func.__name__}' executed in {duration:.4f} seconds")
        return result
    return wrapper

def async_log_execution_time(func):
    """
    Decorator that logs the execution time of an asynchronous function.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Async function '{func.__name__}' executed in {duration:.4f} seconds")
        return result
    return wrapper
