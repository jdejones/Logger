"""Timing helpers for overview logging."""

from __future__ import annotations

import logging
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable, Generator, Optional, TypeVar, cast


DEFAULT_OVERVIEW_LOGGER = "org_logging.overview"


@dataclass(frozen=True)
class TimingResult:
    name: str
    elapsed_ms: float
    run_id: str


def _resolve_logger(logger: Optional[logging.Logger]) -> logging.Logger:
    return logger or logging.getLogger(DEFAULT_OVERVIEW_LOGGER)


def _resolve_run_id(logger: logging.Logger, run_id: Optional[str]) -> str:
    if run_id:
        return run_id
    extra = getattr(logger, "extra", None)
    if isinstance(extra, dict) and extra.get("run_id"):
        return str(extra["run_id"])
    return str(uuid.uuid4())


def _emit_duration(
    *,
    logger: logging.Logger,
    name: str,
    elapsed_ms: float,
    run_id: str,
) -> None:
    logger.info(
        "duration",
        extra={
            "event": "duration",
            "duration_name": name,
            "elapsed_ms": elapsed_ms,
            "run_id": run_id,
        },
    )


def _emit_return_count(
    *,
    logger: logging.Logger,
    name: str,
    count: int,
    run_id: str,
) -> None:
    logger.info(
        "return_count",
        extra={
            "event": "return_count",
            "return_count_name": name,
            "count": count,
            "run_id": run_id,
        },
    )


@contextmanager
def log_timing(
    name: str,
    *,
    run_id: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
) -> Generator[TimingResult, None, None]:
    """Measure elapsed time for a block and log to the overview feed."""
    resolved_logger = _resolve_logger(logger)
    resolved_run_id = _resolve_run_id(resolved_logger, run_id)
    start = time.perf_counter()
    try:
        yield TimingResult(name=name, elapsed_ms=0.0, run_id=resolved_run_id)
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000
        _emit_duration(
            logger=resolved_logger,
            name=name,
            elapsed_ms=elapsed_ms,
            run_id=resolved_run_id,
        )


F = TypeVar("F", bound=Callable[..., object])


def log_duration(
    func: Optional[F] = None,
    *,
    name: Optional[str] = None,
    run_id: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
) -> Callable[[F], F] | F:
    """Decorator for logging function runtime to the overview feed."""

    def decorator(target: F) -> F:
        resolved_name = name or target.__qualname__

        def wrapper(*args: object, **kwargs: object) -> object:
            resolved_logger = _resolve_logger(logger)
            resolved_run_id = _resolve_run_id(resolved_logger, run_id)
            start = time.perf_counter()
            try:
                return target(*args, **kwargs)
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                _emit_duration(
                    logger=resolved_logger,
                    name=resolved_name,
                    elapsed_ms=elapsed_ms,
                    run_id=resolved_run_id,
                )

        wrapper = cast(F, wrapper)
        wrapper.__name__ = getattr(target, "__name__", resolved_name)
        wrapper.__doc__ = target.__doc__
        wrapper.__qualname__ = getattr(target, "__qualname__", resolved_name)
        return wrapper

    if func is not None:
        return decorator(func)

    return decorator


def log_return_count(
    func: Optional[F] = None,
    *,
    name: Optional[str] = None,
    run_id: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
) -> Callable[[F], F] | F:
    """Decorator for logging how many items a function returns."""

    def decorator(target: F) -> F:
        resolved_name = name or target.__qualname__

        def wrapper(*args: object, **kwargs: object) -> object:
            resolved_logger = _resolve_logger(logger)
            resolved_run_id = _resolve_run_id(resolved_logger, run_id)
            result = target(*args, **kwargs)
            if result is None:
                count = 0
            else:
                try:
                    count = len(result)  # type: ignore[arg-type]
                except TypeError:
                    count = 1
            _emit_return_count(
                logger=resolved_logger,
                name=resolved_name,
                count=count,
                run_id=resolved_run_id,
            )
            return result

        wrapper = cast(F, wrapper)
        wrapper.__name__ = getattr(target, "__name__", resolved_name)
        wrapper.__doc__ = target.__doc__
        wrapper.__qualname__ = getattr(target, "__qualname__", resolved_name)
        return wrapper

    if func is not None:
        return decorator(func)

    return decorator
