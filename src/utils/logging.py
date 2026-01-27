"""
Structured Logging Configuration

Uses structlog for structured, JSON-compatible logging that's easy to:
- Debug locally (pretty printed)
- Parse in production (JSON)
- Search and filter (structured fields)
"""

import structlog
import logging
import sys
from typing import Optional


def configure_logging(
    level: str = "INFO",
    json_format: bool = False,
    log_file: Optional[str] = None,
) -> None:
    """
    Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        json_format: If True, output JSON (for production). If False, pretty print (for dev).
        log_file: Optional file path to write logs to.
    """
    # Set up standard logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, level.upper()),
        stream=sys.stdout,
    )

    # Configure structlog processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if json_format:
        # Production: JSON format
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development: Pretty print
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# Pre-configured loggers for common modules
def get_search_logger() -> structlog.stdlib.BoundLogger:
    """Get logger for search operations."""
    return get_logger("rag.search")


def get_agent_logger() -> structlog.stdlib.BoundLogger:
    """Get logger for agent operations."""
    return get_logger("rag.agent")


def get_api_logger() -> structlog.stdlib.BoundLogger:
    """Get logger for API operations."""
    return get_logger("rag.api")


# Initialize with defaults (can be reconfigured later)
configure_logging()
