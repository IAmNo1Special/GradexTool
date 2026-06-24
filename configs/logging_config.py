"""Centralized logging configuration."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(name: str = "GradexTool") -> logging.Logger:
    """Configure logging to file and stdout.

    Args:
        name: Name of the logger to retrieve.

    Returns:
        The logger with the specified name.
    """
    root_logger = logging.getLogger()

    # If root logger is not already configured, configure it
    if not root_logger.handlers:
        root_logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console handler
        try:
            sys.stdout.reconfigure(errors="backslashreplace")  # type: ignore[union-attr]
        except Exception:
            pass
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # File handler
        log_path = Path("logs", "GradexTool.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return logging.getLogger(name)
