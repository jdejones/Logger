"""Utilities for analyzing log data."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any, Iterable


@dataclass(frozen=True)
class DurationStats:
    count: int
    min: float
    max: float
    avg: float


def _read_json_lines(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                entries.append({"raw": line})
    return entries


def load_detail_entries(path: str | Path) -> list[dict[str, Any]]:
    """Load JSONL detail log entries."""
    return _read_json_lines(Path(path))


def load_overview_entries(path: str | Path) -> list[dict[str, Any]]:
    """Load JSONL overview entries (if the overview log is JSONL)."""
    return _read_json_lines(Path(path))


def count_events(entries: Iterable[dict[str, Any]]) -> Counter[str]:
    """Count occurrences by event field."""
    counter: Counter[str] = Counter()
    for entry in entries:
        if isinstance(entry, dict):
            event = entry.get("event")
            if event:
                counter[str(event)] += 1
    return counter


def duration_stats(
    entries: Iterable[dict[str, Any]],
    *,
    unit: str | None = None,
) -> dict[str, DurationStats]:
    """Aggregate duration events by duration_name."""
    values: dict[str, list[float]] = defaultdict(list)
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if entry.get("event") != "duration":
            continue
        if unit and entry.get("unit") != unit:
            continue
        name = entry.get("duration_name")
        elapsed = entry.get("elapsed")
        if name is None or elapsed is None:
            continue
        try:
            values[str(name)].append(float(elapsed))
        except (TypeError, ValueError):
            continue

    stats: dict[str, DurationStats] = {}
    for name, items in values.items():
        stats[name] = DurationStats(
            count=len(items),
            min=min(items),
            max=max(items),
            avg=mean(items),
        )
    return stats


def return_count_stats(entries: Iterable[dict[str, Any]]) -> dict[str, DurationStats]:
    """Aggregate return_count events by return_count_name."""
    values: dict[str, list[float]] = defaultdict(list)
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if entry.get("event") != "return_count":
            continue
        name = entry.get("return_count_name")
        count = entry.get("count")
        if name is None or count is None:
            continue
        try:
            values[str(name)].append(float(count))
        except (TypeError, ValueError):
            continue

    stats: dict[str, DurationStats] = {}
    for name, items in values.items():
        stats[name] = DurationStats(
            count=len(items),
            min=min(items),
            max=max(items),
            avg=mean(items),
        )
    return stats
