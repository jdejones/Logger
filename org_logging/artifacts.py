from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ArtifactMeta:
    path: str
    bytes: int
    hash: str


class ArtifactStore:
    def __init__(self, root: str | Path = "artifacts") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put_bytes(self, data: bytes, *, suffix: str = "") -> ArtifactMeta:
        digest = hashlib.sha256(data).hexdigest()
        filename = f"{digest}{suffix}"
        path = self.root / filename
        path.write_bytes(data)
        return ArtifactMeta(path=str(path), bytes=len(data), hash=digest)

    def put_json(
        self,
        payload: Any,
        *,
        suffix: str = ".json",
        indent: Optional[int] = None,
        sort_keys: bool = True,
    ) -> ArtifactMeta:
        data = json.dumps(payload, indent=indent, sort_keys=sort_keys).encode("utf-8")
        return self.put_bytes(data, suffix=suffix)
