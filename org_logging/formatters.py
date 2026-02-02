import json
import logging
from datetime import datetime, timezone


class JsonlFormatter(logging.Formatter):
    """Format log records as JSON lines suitable for detail logs."""

    def format(self, record: logging.LogRecord) -> str:
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
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)


class OverviewFormatter(logging.Formatter):
    """Human-friendly formatter for overview logs."""

    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s %(levelname)s [%(app)s:%(run_id)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
