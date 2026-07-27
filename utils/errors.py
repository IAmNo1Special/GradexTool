"""Centralized error handling and custom exceptions for GradexTool."""

import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

import discord
from discord import Interaction

logger = logging.getLogger(__name__)


class GradexToolError(Exception):
    """Base exception for GradexTool errors."""

    def __init__(self, message: str, user_message: str | None = None):
        super().__init__(message)
        self.user_message = user_message or message


class ExternalAPIError(GradexToolError):
    """Raised when an external API call fails."""

    def __init__(self, message: str, api_name: str = "external API"):
        super().__init__(
            message, f"Failed to fetch data from {api_name}. Please try again later."
        )
        self.api_name = api_name


class DatabaseError(GradexToolError):
    """Raised when a database operation fails."""

    def __init__(self, message: str, query: str | None = None):
        super().__init__(message, "Database error. Please try again later.")
        self.query = query


class ValidationError(GradexToolError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(message, message)
        self.field = field


class NotFoundError(GradexToolError):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(f"{resource} not found: {identifier}")
        self.resource = resource
        self.identifier = identifier


class RateLimitError(GradexToolError):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: float | None = None):
        msg = "Rate limit exceeded"
        if retry_after:
            msg += f", retry after {retry_after:.1f}s"
        super().__init__(msg, "Too many requests. Please wait a moment and try again.")
        self.retry_after = retry_after


class CircuitBreaker:
    """Circuit breaker pattern for external API calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: type[Exception] = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(
        self, func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any
    ) -> Any:
        if self.state == "OPEN":
            if time.time() - (self.last_failure_time or 0) > self.timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise ExternalAPIError(f"Circuit breaker is OPEN for {func.__name__}")

        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                logger.info("Circuit breaker CLOSED after successful call")
            return result
        except self.expected_exception:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(
                    f"Circuit breaker OPENED after {self.failure_count} failures"
                )
            raise


# Global circuit breakers for external APIs
_revomon_api_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
_immutable_api_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
_pokeapi_breaker = CircuitBreaker(failure_threshold=5, timeout=60)


def get_revomon_breaker() -> CircuitBreaker:
    return _revomon_api_breaker


def get_immutable_breaker() -> CircuitBreaker:
    return _immutable_api_breaker


def get_pokeapi_breaker() -> CircuitBreaker:
    return _pokeapi_breaker


async def handle_interaction_error(
    interaction: Interaction,
    error: Exception,
    ephemeral: bool = True,
) -> None:
    """Handle errors in interaction callbacks."""
    if isinstance(error, GradexToolError):
        user_msg = error.user_message
        logger.warning(f"Handled error: {error}")
    elif isinstance(error, discord.app_commands.CommandInvokeError):
        original = error.original
        if isinstance(original, GradexToolError):
            user_msg = original.user_message
            logger.warning(f"Handled error: {original}")
        else:
            user_msg = "An unexpected error occurred. Please try again later."
            logger.exception(f"Unhandled error in interaction: {error}")
    else:
        user_msg = "An unexpected error occurred. Please try again later."
        logger.exception(f"Unhandled error in interaction: {error}")

    try:
        if interaction.response.is_done():
            await interaction.followup.send(user_msg, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(user_msg, ephemeral=ephemeral)
    except discord.NotFound:
        logger.warning("Could not send error response: interaction expired")
    except Exception as e:
        logger.exception(f"Failed to send error response: {e}")


def setup_logging(level: int = logging.INFO) -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("gradextool.log", encoding="utf-8"),
        ],
    )

    # Reduce noise from third-party libraries
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("discord.http").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


class ErrorReporter:
    """Collect and report errors for monitoring."""

    def __init__(self) -> None:
        self.error_counts: dict[str, int] = {}
        self.last_errors: list[dict[str, Any]] = []
        self.max_errors = 100

    def record(self, error: Exception, context: dict[str, Any] | None = None) -> None:
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        error_info = {
            "type": error_type,
            "message": str(error),
            "timestamp": time.time(),
            "context": context or {},
        }
        self.last_errors.append(error_info)
        if len(self.last_errors) > self.max_errors:
            self.last_errors.pop(0)

    def get_stats(self) -> dict[str, Any]:
        return {
            "counts": self.error_counts.copy(),
            "recent": self.last_errors[-10:],
        }

    def reset(self) -> None:
        self.error_counts.clear()
        self.last_errors.clear()


# Global error reporter
error_reporter = ErrorReporter()
