"""
Tests for logger_config.py module
"""

import pytest
import logging
import os
from logger_config import setup_logging, get_logger


class TestSetupLogging:
    """Tests for setup_logging function"""

    def test_setup_logging_default(self, temp_dir):
        """Test setting up logging with default parameters"""
        log_file = os.path.join(temp_dir, 'test.log')
        logger = setup_logging(log_file=log_file)

        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.INFO

    def test_setup_logging_debug_level(self, temp_dir):
        """Test setting up logging with DEBUG level"""
        log_file = os.path.join(temp_dir, 'debug.log')
        logger = setup_logging(log_file=log_file, log_level='DEBUG')

        assert logger.level == logging.DEBUG

    def test_setup_logging_creates_file(self, temp_dir):
        """Test that logging creates the log file"""
        log_file = os.path.join(temp_dir, 'created.log')
        logger = setup_logging(log_file=log_file)

        # Write a log message
        logger.info("Test message")

        # Verify file was created
        assert os.path.exists(log_file)

    def test_setup_logging_writes_messages(self, temp_dir):
        """Test that log messages are written to file"""
        log_file = os.path.join(temp_dir, 'messages.log')
        logger = setup_logging(log_file=log_file)

        test_message = "Test log message"
        logger.info(test_message)

        # Read log file and verify message
        with open(log_file, 'r') as f:
            log_content = f.read()

        assert test_message in log_content


class TestGetLogger:
    """Tests for get_logger function"""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance"""
        logger = get_logger('test_module')

        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test_module'

    def test_get_logger_different_names(self):
        """Test getting loggers with different names"""
        logger1 = get_logger('module1')
        logger2 = get_logger('module2')

        assert logger1.name == 'module1'
        assert logger2.name == 'module2'
        assert logger1 is not logger2

    def test_get_logger_same_name_returns_same_logger(self):
        """Test that getting the same logger name returns the same instance"""
        logger1 = get_logger('same_module')
        logger2 = get_logger('same_module')

        assert logger1 is logger2


class TestLoggingLevels:
    """Tests for different logging levels"""

    def test_info_level_logs_info(self, temp_dir):
        """Test that INFO level logs info messages"""
        log_file = os.path.join(temp_dir, 'info.log')
        logger = setup_logging(log_file=log_file, log_level='INFO')

        logger.info("Info message")
        logger.debug("Debug message")  # Should not appear

        with open(log_file, 'r') as f:
            content = f.read()

        assert "Info message" in content
        assert "Debug message" not in content

    def test_debug_level_logs_all(self, temp_dir):
        """Test that DEBUG level logs all messages"""
        log_file = os.path.join(temp_dir, 'debug_all.log')
        logger = setup_logging(log_file=log_file, log_level='DEBUG')

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")

        with open(log_file, 'r') as f:
            content = f.read()

        assert "Debug message" in content
        assert "Info message" in content
        assert "Warning message" in content

    def test_error_level_logs_errors_only(self, temp_dir):
        """Test that ERROR level logs only errors and critical"""
        log_file = os.path.join(temp_dir, 'errors.log')
        logger = setup_logging(log_file=log_file, log_level='ERROR')

        logger.info("Info message")  # Should not appear
        logger.warning("Warning message")  # Should not appear
        logger.error("Error message")
        logger.critical("Critical message")

        with open(log_file, 'r') as f:
            content = f.read()

        assert "Info message" not in content
        assert "Warning message" not in content
        assert "Error message" in content
        assert "Critical message" in content
