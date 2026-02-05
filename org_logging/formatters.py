import json
import logging
from datetime import datetime, timezone


class JsonlFormatter(logging.Formatter):
    """Format log records as JSON lines suitable for detail logs."""

    def format(self, record: logging.LogRecord) -> str:
        # logging allows arbitrary keys via `extra={...}`. We want to persist these
        # structured fields (e.g. `event`, `duration_name`, etc.) into JSONL so
        # downstream consumers can analyze them.
        standard_attrs = {
            # Core LogRecord attributes
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            # Added/derived by logging during formatting
            "message",
            "asctime",
            # Python 3.12+ may include this when using asyncio tasks
            "taskName",
        }

        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "app": getattr(record, "app", None),
            "run_id": getattr(record, "run_id", None),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        # Merge any `extra` fields at the top-level (without clobbering core keys).
        for key, value in record.__dict__.items():
            if key in standard_attrs or key in log_entry:
                continue
            log_entry[key] = value

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        # Avoid formatter crashes if an extra field isn't JSON-serializable.
        return json.dumps(log_entry, ensure_ascii=False, default=str)


class OverviewFormatter(logging.Formatter):
    """Human-friendly formatter for overview logs."""

    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s %(levelname)s [%(app)s:%(run_id)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
