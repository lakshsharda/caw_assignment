import json
import logging
import os
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def resolve_log_level_name() -> str:
    return os.environ.get("LOG_LEVEL", "info")


def resolve_log_level() -> int:
    level_name = resolve_log_level_name().upper()
    return getattr(logging, level_name, logging.INFO)


def sanitize_for_logging(value: Any) -> Any:
    """Sanitize values for safe logging by removing control characters that could enable log injection."""
    if isinstance(value, str):
        # Remove control characters (ASCII < 32, except tab which is safe)
        # Replace with escaped hex representation for visibility
        sanitized = "".join(
            char if ord(char) >= 32 or char == "\t" else f"\\x{ord(char):02x}"
            for char in value
        )
        return sanitized
    elif isinstance(value, dict):
        return {k: sanitize_for_logging(v) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return [sanitize_for_logging(item) for item in value]
    return value


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
                "+00:00", "Z"
            ),
            "level": record.levelname.lower(),
            "service": "api",
            "msg": record.getMessage(),
        }
        req_id = request_id_ctx.get()
        if req_id:
            payload["req_id"] = req_id
        extra_fields = getattr(record, "extra_fields", None)
        if isinstance(extra_fields, dict):
            # Sanitize all extra fields to prevent log injection
            sanitized_fields = sanitize_for_logging(extra_fields)
            payload.update(sanitized_fields)
        return json.dumps(payload, default=str)


def get_logger() -> logging.Logger:
    return logging.getLogger("linkops.api")


def setup_logging() -> logging.Logger:
    logger = get_logger()
    if logger.handlers:
        return logger

    level = resolve_log_level()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLogFormatter())
    handler.setLevel(level)  # Set handler level explicitly
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger


def log_event(level: int, message: str, **fields: Any) -> None:
    logger = get_logger()
    logger.log(level, message, extra={"extra_fields": fields})


def new_request_id() -> str:
    return f"r-{uuid.uuid4().hex[:4]}"
