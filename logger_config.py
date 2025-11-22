#!/usr/bin/env python3
"""
Logging configuration for Obsidian Auto-Linker
Replaces print() statements with proper logging
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(log_level: str = "INFO", log_file: str = "obsidian_linker.log", enable_file_logging: bool = True):
    """
    Set up logging configuration

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        enable_file_logging: Whether to write logs to file
    """
    # Create logger
    logger = logging.getLogger("obsidian_linker")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    # Console handler (for user-facing output)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler (for detailed logs)
    if enable_file_logging:
        try:
            log_path = Path(log_file)
            if log_path.parent:
                log_path.parent.mkdir(parents=True, exist_ok=True)

            # Rotating file handler (max 10MB, keep 5 backups)
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create log file: {e}")

    # Prevent propagation to root logger
    logger.propagate = False

    return logger

def get_logger(name: str = "obsidian_linker") -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)

# Default logger instance
logger = get_logger()

class DashboardLogHandler(logging.Handler):
    """
    Custom log handler that forwards logs to the dashboard
    """

    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard

    def emit(self, record):
        """Emit a log record to the dashboard"""
        try:
            msg = self.format(record)

            # Add to activity log
            if record.levelno >= logging.ERROR:
                self.dashboard.add_error(record.levelname, record.getMessage())
            elif record.levelno >= logging.WARNING:
                self.dashboard.add_activity(f"⚠️  {record.getMessage()}", success=False)
            elif record.levelno >= logging.INFO:
                # Only add important INFO messages to activity
                if any(keyword in record.getMessage().lower() for keyword in ['processed', 'completed', 'started', 'saved']):
                    self.dashboard.add_activity(record.getMessage(), success=True)
        except Exception:
            self.handleError(record)

if __name__ == "__main__":
    # Test logging
    test_logger = setup_logging(log_level="DEBUG")

    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    test_logger.critical("This is a critical message")

    print(f"\nLog file created: obsidian_linker.log")

