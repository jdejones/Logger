import logging
import uuid
from pathlib import Path
from typing import Optional

from .formatters import JsonlFormatter, OverviewFormatter

_DEFAULT_CONTEXT = {"app": None, "run_id": None}


class ContextAdapter(logging.LoggerAdapter):
    """LoggerAdapter that injects app/run_id context into log records."""

    def process(self, msg, kwargs):
        extra = dict(self.extra)
        if "extra" in kwargs:
            extra.update(kwargs["extra"])
        kwargs["extra"] = extra
        return msg, kwargs


def configure_logging(
    app_name: str,
    log_dir: str | Path,
    run_id: Optional[str] = None,
    overview_filename: str = "overview.log",
    detail_filename: str = "detail.jsonl",
    overview_level: int = logging.INFO,
    detail_level: int = logging.DEBUG,
    console_level: int = logging.INFO,
) -> str:
    """Configure logging with overview, detail JSONL, and console handlers.

    Returns the run_id used for this configuration.
    """
    resolved_run_id = run_id or uuid.uuid4().hex
    _DEFAULT_CONTEXT.update({"app": app_name, "run_id": resolved_run_id})

    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    overview_handler = logging.FileHandler(log_path / overview_filename)
    overview_handler.setLevel(overview_level)
    overview_handler.setFormatter(OverviewFormatter())

    detail_handler = logging.FileHandler(log_path / detail_filename)
    detail_handler.setLevel(detail_level)
    detail_handler.setFormatter(JsonlFormatter())

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(OverviewFormatter())

    root_logger.addHandler(overview_handler)
    root_logger.addHandler(detail_handler)
    root_logger.addHandler(console_handler)

    return resolved_run_id


def get_logger(name: str, app: Optional[str] = None, run_id: Optional[str] = None) -> ContextAdapter:
    """Return a LoggerAdapter with app/run_id injected into log records."""
    context = {
        "app": app or _DEFAULT_CONTEXT.get("app"),
        "run_id": run_id or _DEFAULT_CONTEXT.get("run_id"),
    }
    return ContextAdapter(logging.getLogger(name), context)
