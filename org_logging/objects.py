from __future__ import annotations

import json
from io import BytesIO
from typing import Any, Callable, Dict, Optional

from .artifacts import ArtifactMeta, ArtifactStore


def _emit(logger: Any, payload: Dict[str, Any]) -> None:
    if hasattr(logger, "info"):
        logger.info(payload)
    elif callable(logger):
        logger(payload)
    else:
        raise TypeError("logger must be a logging.Logger or callable")


def _json_bytes(obj: Any) -> bytes:
    return json.dumps(obj).encode("utf-8")


def _dataframe_to_parquet_bytes(df: Any) -> Optional[bytes]:
    try:
        buffer = BytesIO()
        df.to_parquet(buffer, index=False)
        return buffer.getvalue()
    except Exception:
        return None


def log_object(
    logger: Any,
    key: str,
    obj: Any,
    *,
    artifact_store: Optional[ArtifactStore] = None,
    inline_limit: int = 2048,
    event: str = "object",
) -> Dict[str, Any]:
    store = artifact_store or ArtifactStore()
    meta: Dict[str, Any] = {}
    artifact_path: Optional[str] = None
    type_label = type(obj).__name__

    try:
        import pandas as pd  # type: ignore

        if isinstance(obj, pd.DataFrame):
            parquet_bytes = _dataframe_to_parquet_bytes(obj)
            if parquet_bytes is not None:
                artifact = store.put_bytes(parquet_bytes, suffix=".parquet")
                artifact_path = artifact.path
                type_label = "parquet"
                meta.update(
                    {
                        "rows": int(obj.shape[0]),
                        "columns": int(obj.shape[1]),
                        "bytes": artifact.bytes,
                        "hash": artifact.hash,
                    }
                )
                payload = {
                    "event": event,
                    "key": key,
                    "type": type_label,
                    "artifact_path": artifact_path,
                    "meta": meta,
                }
                _emit(logger, payload)
                return payload
    except Exception:
        pass

    json_bytes = _json_bytes(obj)
    if len(json_bytes) <= inline_limit:
        meta.update({"bytes": len(json_bytes), "value": obj})
        payload = {
            "event": event,
            "key": key,
            "type": "inline_json",
            "artifact_path": None,
            "meta": meta,
        }
        _emit(logger, payload)
        return payload

    artifact = store.put_bytes(json_bytes, suffix=".json")
    artifact_path = artifact.path
    meta.update({"bytes": artifact.bytes, "hash": artifact.hash})
    payload = {
        "event": event,
        "key": key,
        "type": "artifact_json",
        "artifact_path": artifact_path,
        "meta": meta,
    }
    _emit(logger, payload)
    return payload
