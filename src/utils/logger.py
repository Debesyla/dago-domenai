"""Logging setup and safe execution decorators"""
import logging
import functools
import traceback
from typing import Callable, Any, TypeVar
from pathlib import Path


T = TypeVar('T')


def setup_logger(
    name: str = "domain_analyzer",
    level: str = "INFO",
    log_dir: str = "./logs",
    max_size_mb: int = 5,
    backup_count: int = 5
) -> logging.Logger:
    """
    Configure and return a logger with file and console handlers.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        max_size_mb: Max size of each log file in MB
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create log directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # File handler with rotation
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        Path(log_dir) / f"{name}.log",
        maxBytes=max_size_mb * 1024 * 1024,
        backupCount=backup_count
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def safe_run(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator for safe synchronous function execution with error logging.
    
    Returns None on exception instead of crashing.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger("domain_analyzer")
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.debug(traceback.format_exc())
            return None
    return wrapper


def safe_run_async(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator for safe async function execution with error logging.
    
    Returns None on exception instead of crashing.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger("domain_analyzer")
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.debug(traceback.format_exc())
            return None
    return wrapper
