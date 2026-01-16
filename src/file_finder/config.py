"""Configuration management for FileFinder library."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """Configuration class for FileFinder."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        # Logging configuration
        self.log_level: str = os.getenv("FILE_FINDER_LOG_LEVEL", "INFO")
        self.log_format: str = os.getenv(
            "FILE_FINDER_LOG_FORMAT",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.log_file: str | None = os.getenv("FILE_FINDER_LOG_FILE")

        # Search configuration
        self.default_follow_symlinks: bool = (
            os.getenv("FILE_FINDER_FOLLOW_SYMLINKS", "false").lower() == "true"
        )
        self.default_max_depth: int | None = self._get_int_env("FILE_FINDER_MAX_DEPTH")
        self.default_max_results: int | None = self._get_int_env("FILE_FINDER_MAX_RESULTS")

        # Performance configuration
        self.enable_caching: bool = (
            os.getenv("FILE_FINDER_ENABLE_CACHING", "false").lower() == "true"
        )
        self.cache_size: int = int(os.getenv("FILE_FINDER_CACHE_SIZE", "1000"))

    @staticmethod
    def _get_int_env(key: str) -> int | None:
        """Get integer value from environment variable."""
        value = os.getenv(key)
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            return None


# Global configuration instance
config = Config()


def setup_logging(
    level: str | None = None,
    format_string: str | None = None,
    log_file: str | None = None,
) -> None:
    """
    Set up logging for the FileFinder library.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Format string for log messages
        log_file: Optional file path to write logs to
    """
    level = level or config.log_level
    format_string = format_string or config.log_format
    log_file = log_file or config.log_file

    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger for the file_finder package
    logger = logging.getLogger("file_finder")
    logger.setLevel(numeric_level)

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_formatter = logging.Formatter(format_string)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Add file handler if log_file is specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the FileFinder library.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    # Ensure logging is set up
    if not logging.getLogger("file_finder").handlers:
        setup_logging()

    return logging.getLogger(f"file_finder.{name}")


# Set up logging on module import
setup_logging()
