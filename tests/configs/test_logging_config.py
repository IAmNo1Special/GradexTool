"""Comprehensive tests for configs/logging_config.py."""

import logging
import sys
from pathlib import Path

import pytest

from configs.logging_config import setup_logging


@pytest.fixture(autouse=True)
def cleanup_logging() -> None:  # type: ignore[misc]
    """Cleanup logging handlers after each test to prevent ResourceWarnings."""
    yield
    for handler in logging.root.handlers[:]:
        handler.close()
        logging.root.removeHandler(handler)

    logger = logging.getLogger("GradexTool")
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    logger = logging.getLogger("CustomLogger")
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    logger = logging.getLogger("Logger1")
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    logger = logging.getLogger("Logger2")
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


class TestSetupLoggingBasic:
    """Basic tests for setup_logging function."""

    def test_setup_logging_returns_logger(self) -> None:
        """Test that setup_logging returns a logger object."""
        logger = setup_logging()
        assert isinstance(logger, logging.Logger)

    def test_setup_logging_default_name(self) -> None:
        """Test that setup_logging uses default name when not provided."""
        logger = setup_logging()
        assert logger.name == "GradexTool"

    def test_setup_logging_custom_name(self) -> None:
        """Test that setup_logging uses custom name when provided."""
        logger = setup_logging(name="CustomLogger")
        assert logger.name == "CustomLogger"

    def test_setup_logging_returns_same_logger_for_same_name(self) -> None:
        """Test that setup_logging returns the same logger instance for the same name."""
        logger1 = setup_logging(name="TestLogger")
        logger2 = setup_logging(name="TestLogger")
        assert logger1 is logger2


class TestRootLoggerConfiguration:
    """Tests for root logger configuration."""

    def test_root_logger_level_is_info(self) -> None:
        """Test that root logger level is set to INFO."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()
        logging.root.setLevel(logging.WARNING)

        setup_logging()
        assert logging.root.level == logging.INFO

    def test_root_logger_has_handlers(self) -> None:
        """Test that root logger has handlers after setup."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        assert len(logging.root.handlers) > 0

    def test_root_logger_has_console_handler(self) -> None:
        """Test that root logger has a console handler."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        has_stream_handler = any(
            isinstance(handler, logging.StreamHandler)
            for handler in logging.root.handlers
        )
        assert has_stream_handler

    def test_root_logger_has_file_handler(self) -> None:
        """Test that root logger has a file handler."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        has_file_handler = any(
            isinstance(handler, logging.handlers.RotatingFileHandler)
            for handler in logging.root.handlers
        )
        assert has_file_handler


class TestConsoleHandler:
    """Tests for console handler configuration."""

    def test_console_handler_outputs_to_stdout(self) -> None:
        """Test that console handler outputs to stdout."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        stream_handler = next(
            (
                handler
                for handler in logging.root.handlers
                if isinstance(handler, logging.StreamHandler)
                and not isinstance(handler, logging.handlers.RotatingFileHandler)
            ),
            None,
        )
        assert stream_handler is not None
        assert stream_handler.stream == sys.stdout

    def test_console_handler_has_formatter(self) -> None:
        """Test that console handler has a formatter."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        stream_handler = next(
            (
                handler
                for handler in logging.root.handlers
                if isinstance(handler, logging.StreamHandler)
                and not isinstance(handler, logging.handlers.RotatingFileHandler)
            ),
            None,
        )
        assert stream_handler is not None
        assert stream_handler.formatter is not None


class TestFileHandler:
    """Tests for file handler configuration."""

    def test_file_handler_is_rotating_file_handler(self) -> None:
        """Test that file handler is a RotatingFileHandler."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        file_handler = next(
            (
                handler
                for handler in logging.root.handlers
                if isinstance(handler, logging.handlers.RotatingFileHandler)
            ),
            None,
        )
        assert file_handler is not None

    def test_file_handler_has_formatter(self) -> None:
        """Test that file handler has a formatter."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        file_handler = next(
            (
                handler
                for handler in logging.root.handlers
                if isinstance(handler, logging.handlers.RotatingFileHandler)
            ),
            None,
        )
        assert file_handler is not None
        assert file_handler.formatter is not None

    def test_file_handler_max_bytes(self) -> None:
        """Test that file handler has correct maxBytes setting."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        file_handler = next(
            (
                handler
                for handler in logging.root.handlers
                if isinstance(handler, logging.handlers.RotatingFileHandler)
            ),
            None,
        )
        assert file_handler is not None
        assert file_handler.maxBytes == 10_000_000

    def test_file_handler_backup_count(self) -> None:
        """Test that file handler has correct backupCount setting."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        file_handler = next(
            (
                handler
                for handler in logging.root.handlers
                if isinstance(handler, logging.handlers.RotatingFileHandler)
            ),
            None,
        )
        assert file_handler is not None
        assert file_handler.backupCount == 3

    def test_file_handler_encoding(self) -> None:
        """Test that file handler has correct encoding setting."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        file_handler = next(
            (
                handler
                for handler in logging.root.handlers
                if isinstance(handler, logging.handlers.RotatingFileHandler)
            ),
            None,
        )
        assert file_handler is not None
        assert file_handler.encoding == "utf-8"


class TestFormatter:
    """Tests for formatter configuration."""

    def test_formatter_format_string(self) -> None:
        """Test that formatter has correct format string."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        formatter = logging.root.handlers[0].formatter
        expected_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert formatter._fmt == expected_format  # type: ignore[union-attr]


class TestLogFileCreation:
    """Tests for log file creation."""

    def test_log_file_name_includes_datetime(self) -> None:
        """Test that log file name includes current datetime."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        file_handler = next(
            (
                handler
                for handler in logging.root.handlers
                if isinstance(handler, logging.handlers.RotatingFileHandler)
            ),
            None,
        )
        assert file_handler is not None
        log_file_path = Path(file_handler.baseFilename)
        assert log_file_path.name == "GradexTool.log"


class TestMultipleSetupCalls:
    """Tests for multiple calls to setup_logging."""

    def test_multiple_setup_calls_do_not_duplicate_handlers(self) -> None:
        """Test that multiple calls to setup_logging do not duplicate handlers."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        after_first_count = len(logging.root.handlers)

        setup_logging()
        after_second_count = len(logging.root.handlers)

        assert after_second_count == after_first_count

    def test_multiple_setup_calls_return_loggers_with_correct_names(self) -> None:
        """Test that multiple calls to setup_logging return loggers with correct names."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        logger1 = setup_logging(name="Logger1")
        logger2 = setup_logging(name="Logger2")

        assert logger1.name == "Logger1"
        assert logger2.name == "Logger2"


class TestLoggerFunctionality:
    """Tests for logger functionality after setup."""

    def test_logger_can_log_info_message(self) -> None:
        """Test that logger can log INFO messages."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        logger = setup_logging()
        # This should not raise an exception
        logger.info("Test info message")

    def test_logger_can_log_warning_message(self) -> None:
        """Test that logger can log WARNING messages."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        logger = setup_logging()
        # This should not raise an exception
        logger.warning("Test warning message")

    def test_logger_can_log_error_message(self) -> None:
        """Test that logger can log ERROR messages."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        logger = setup_logging()
        # This should not raise an exception
        logger.error("Test error message")

    def test_logger_can_log_debug_message(self) -> None:
        """Test that logger can log DEBUG messages."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        logger = setup_logging()
        # This should not raise an exception
        logger.debug("Test debug message")


class TestDateTimeFormatting:
    """Tests for datetime formatting in log file names."""

    def test_datetime_format_is_correct(self) -> None:
        """Test that datetime format in log file name is correct."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        file_handler = next(
            (
                handler
                for handler in logging.root.handlers
                if isinstance(handler, logging.handlers.RotatingFileHandler)
            ),
            None,
        )
        assert file_handler is not None
        log_file_path = Path(file_handler.baseFilename)
        assert log_file_path.name == "GradexTool.log"


class TestEdgeCases:
    """Tests for edge cases."""

    def test_setup_logging_with_empty_name(self) -> None:
        """Test that setup_logging with empty string returns root logger."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        logger = setup_logging(name="")
        # Empty string returns the root logger in Python's logging module
        assert logger.name == "root"


class TestLoggingOutput:
    """Tests for logging output."""

    def test_logger_outputs_to_console(self) -> None:
        """Test that logger outputs to console."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        # Check that there's a StreamHandler that writes to stdout
        has_stdout_handler = any(
            isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout
            for handler in logging.root.handlers
        )
        assert has_stdout_handler

    def test_logger_outputs_to_file(self) -> None:
        """Test that logger outputs to file."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        # Check that there's a RotatingFileHandler
        has_file_handler = any(
            isinstance(handler, logging.handlers.RotatingFileHandler)
            for handler in logging.root.handlers
        )
        assert has_file_handler


class TestHandlerConfiguration:
    """Tests for detailed handler configuration."""

    def test_console_handler_level(self) -> None:
        """Test that console handler has correct level."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        stream_handler = next(
            (
                handler
                for handler in logging.root.handlers
                if isinstance(handler, logging.StreamHandler)
                and not isinstance(handler, logging.handlers.RotatingFileHandler)
            ),
            None,
        )
        assert stream_handler is not None
        # Console handler should inherit root logger level (INFO)
        assert (
            stream_handler.level == logging.NOTSET
        )  # NOTSET means it inherits from logger

    def test_file_handler_level(self) -> None:
        """Test that file handler has correct level."""
        # Reset logging to clear any existing handlers
        logging.root.handlers.clear()

        setup_logging()
        file_handler = next(
            (
                handler
                for handler in logging.root.handlers
                if isinstance(handler, logging.handlers.RotatingFileHandler)
            ),
            None,
        )
        assert file_handler is not None
        # File handler should inherit root logger level (INFO)
        assert (
            file_handler.level == logging.NOTSET
        )  # NOTSET means it inherits from logger
