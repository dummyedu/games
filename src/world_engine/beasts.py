from __future__ import annotations

from pathlib import Path
from typing import Any

from world_engine.io import WorldDataError, load_yaml


def load_beast_template(ruleset_path: Path, beast_id: str) -> dict[str, Any]:
    content_root = ruleset_path / "content" / "beasts"
    if not content_root.exists():
        raise WorldDataError(f"beast content directory does not exist: {content_root}")

    for path in content_root.rglob("*.yaml"):
        data = load_yaml(path)
        if data.get("id") == beast_id:
            return data

    raise WorldDataError(f"beast template does not exist: {beast_id}")
