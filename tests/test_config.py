"""Tests for configuration module."""

import logging

from file_finder.config import Config, get_logger, setup_logging


class TestConfig:
    """Test Config class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        assert config.log_level == "INFO"
        assert "%(asctime)s" in config.log_format
        assert config.default_follow_symlinks is False

    def test_config_from_environment(self, monkeypatch):
        """Test configuration from environment variables."""
        monkeypatch.setenv("FILE_FINDER_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("FILE_FINDER_FOLLOW_SYMLINKS", "true")
        monkeypatch.setenv("FILE_FINDER_MAX_DEPTH", "5")

        config = Config()
        assert config.log_level == "DEBUG"
        assert config.default_follow_symlinks is True
        assert config.default_max_depth == 5

    def test_config_invalid_int_env(self, monkeypatch):
        """Test handling of invalid integer environment variables."""
        monkeypatch.setenv("FILE_FINDER_MAX_DEPTH", "invalid")

        config = Config()
        assert config.default_max_depth is None


class TestLogging:
    """Test logging configuration."""

    def test_setup_logging_default(self):
        """Test default logging setup."""
        setup_logging()
        logger = logging.getLogger("file_finder")
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0

    def test_setup_logging_custom_level(self):
        """Test logging setup with custom level."""
        setup_logging(level="DEBUG")
        logger = logging.getLogger("file_finder")
        assert logger.level == logging.DEBUG

    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = get_logger("test")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "file_finder.test"

    def test_logging_no_propagate(self):
        """Test that logger doesn't propagate to root."""
        setup_logging()
        logger = logging.getLogger("file_finder")
        assert logger.propagate is False
