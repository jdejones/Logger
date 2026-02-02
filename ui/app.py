from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request


@dataclass
class LogConfig:
    overview_path: Path
    detail_path: Path | None
    artifact_path: Path | None
    max_entries: int


def _default_log_dir() -> Path:
    return Path(os.getenv("LOG_DIR", "./logs")).expanduser()


def _default_log_filename(env_key: str, fallback: str) -> str:
    return os.getenv(env_key, fallback)


def load_config() -> LogConfig:
    log_dir = _default_log_dir()
    overview_path = os.getenv("OVERVIEW_LOG_PATH")
    if overview_path:
        overview_path = Path(overview_path).expanduser()
    else:
        overview_filename = _default_log_filename("OVERVIEW_LOG_FILENAME", "overview.log")
        overview_path = log_dir / overview_filename
    detail_path_value = os.getenv("DETAIL_LOG_PATH")
    artifact_path_value = os.getenv("ARTIFACT_METADATA_PATH")
    max_entries = int(os.getenv("LOG_MAX_ENTRIES", "200"))

    return LogConfig(
        overview_path=overview_path,
        detail_path=Path(detail_path_value).expanduser() if detail_path_value else None,
        artifact_path=Path(artifact_path_value).expanduser() if artifact_path_value else None,
        max_entries=max_entries,
    )


app = Flask(__name__)


@app.route("/")
def index() -> str:
    config = load_config()
    return render_template(
        "index.html",
        overview_path=str(config.overview_path),
        detail_path=str(config.detail_path) if config.detail_path else "",
        artifact_path=str(config.artifact_path) if config.artifact_path else "",
    )


def _read_overview_from_offset(path: Path, offset: int, max_entries: int) -> dict[str, Any]:
    if not path.exists():
        return {"lines": [], "offset": 0, "error": f"Overview log not found: {path}"}

    size = path.stat().st_size
    if offset < 0 or offset > size:
        offset = 0

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        handle.seek(offset)
        lines = handle.read().splitlines()
        new_offset = handle.tell()

    if max_entries and len(lines) > max_entries:
        lines = lines[-max_entries:]

    return {"lines": lines, "offset": new_offset, "error": None}


def _read_overview_tail(path: Path, max_entries: int) -> dict[str, Any]:
    if not path.exists():
        return {"lines": [], "offset": 0, "error": f"Overview log not found: {path}"}

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        lines = handle.read().splitlines()
        offset = handle.tell()

    if max_entries and len(lines) > max_entries:
        lines = lines[-max_entries:]

    return {"lines": lines, "offset": offset, "error": None}


@app.route("/api/overview")
def overview() -> Any:
    config = load_config()
    offset_value = request.args.get("offset")
    try:
        offset = int(offset_value) if offset_value is not None else None
    except ValueError:
        offset = None

    if offset is None:
        payload = _read_overview_tail(config.overview_path, config.max_entries)
    else:
        payload = _read_overview_from_offset(config.overview_path, offset, config.max_entries)

    return jsonify(payload)


def _read_jsonl(path: Path, max_entries: int, entry_id: str | None) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        lines = handle.read().splitlines()

    if max_entries and len(lines) > max_entries:
        lines = lines[-max_entries:]

    entries: list[dict[str, Any]] = []
    for line in lines:
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            item = {"raw": line}

        if entry_id:
            if isinstance(item, dict) and str(item.get("id")) == entry_id:
                entries.append(item)
            else:
                continue
        else:
            entries.append(item)

    return entries


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"raw": path.read_text(encoding="utf-8", errors="replace")}


@app.route("/api/detail")
def detail() -> Any:
    config = load_config()
    detail_path_value = request.args.get("detail_path")
    artifact_path_value = request.args.get("artifact_path")
    entry_id = request.args.get("id")

    detail_path = Path(detail_path_value).expanduser() if detail_path_value else config.detail_path
    artifact_path = (
        Path(artifact_path_value).expanduser() if artifact_path_value else config.artifact_path
    )

    detail_entries: list[dict[str, Any]] = []
    artifact_metadata: dict[str, Any] | None = None

    if detail_path:
        detail_entries = _read_jsonl(detail_path, config.max_entries, entry_id)

    if artifact_path:
        artifact_metadata = _read_json(artifact_path)

    return jsonify(
        {
            "detail_entries": detail_entries,
            "artifact_metadata": artifact_metadata,
            "detail_path": str(detail_path) if detail_path else "",
            "artifact_path": str(artifact_path) if artifact_path else "",
        }
    )


@app.route("/api/config")
def config() -> Any:
    config = load_config()
    return jsonify(
        {
            "overview_path": str(config.overview_path),
            "detail_path": str(config.detail_path) if config.detail_path else "",
            "artifact_path": str(config.artifact_path) if config.artifact_path else "",
            "max_entries": config.max_entries,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
