# utils/logging.py
import logging
import os
import sys
import time
import json
from logging.handlers import RotatingFileHandler


class CustomFormatter(logging.Formatter):
    """Custom formatter that outputs JSON formatted logs."""

    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Add extra fields from the record
        for key, value in record.__dict__.items():
            if key not in [
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "id",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            ]:
                log_record[key] = value

        return json.dumps(log_record)


def setup_logging(name=None, log_file=None):
    """
    Set up logging configuration.

    Args:
        name: Logger name (None for root logger)
        log_file: Log file path (None for no file logging)

    Returns:
        Configured logger
    """
    # Get log level from environment
    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Determine format based on environment
    if os.getenv("LOG_FORMAT", "").lower() == "json":
        formatter = CustomFormatter()
    else:
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add file handler if log file specified
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10 MB
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Create application logger
app_logger = setup_logging(
    name="legal_assistant", log_file=os.path.join("logs", "app.log")
)

# Create request logger
request_logger = setup_logging(
    name="legal_assistant.request", log_file=os.path.join("logs", "request.log")
)


class RequestLogMiddleware:
    """Middleware to log API requests and responses."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        start_time = time.time()

        # Process the request with the actual app
        await self.app(scope, receive, send)

        # Log request details
        process_time = time.time() - start_time
        path = scope.get("path", "")
        method = scope.get("method", "")

        request_logger.info(
            f"Request processed",
            extra={
                "path": path,
                "method": method,
                "process_time_ms": round(process_time * 1000, 2),
            },
        )
