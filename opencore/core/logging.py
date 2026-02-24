import logging
import json
import sys
from datetime import datetime, timezone
from opencore.config import settings
from opencore.core.context import request_id_ctx


class RequestIdFilter(logging.Filter):
    """
    Filter that injects the current request ID into the log record.
    """
    def filter(self, record):
        record.request_id = request_id_ctx.get()
        return True


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
        }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Include specific extra fields if present (e.g., request_id, user_id)
        # We avoid blindly dumping everything to prevent serialization errors
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id

        return json.dumps(log_record)


def configure_logging():
    """
    Configures the root logger based on the application environment.
    """
    root_logger = logging.getLogger()

    # Remove existing handlers to avoid duplicates
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    # Determine log level
    log_level_str = settings.log_level.upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    root_logger.setLevel(log_level)

    # Create handler (StreamHandler to stdout/stderr is standard)
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())

    # Set formatter based on environment
    if settings.app_env == "production":
        formatter = JSONFormatter()
    else:
        # Human-readable format for development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - [%(request_id)s] - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Log that logging is configured
    logging.info(
        f"Logging configured. Environment: {settings.app_env}, "
        f"Level: {log_level_str}"
    )
