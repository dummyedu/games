from __future__ import annotations

from pathlib import Path
from typing import Any

from world_engine.io import load_yaml


def load_entity_index(world_root: Path) -> dict[str, dict[str, Any]]:
    path = world_root / "indexes" / "entities.yaml"
    data = load_yaml(path)
    entities = data.get("entities", {})
    if not isinstance(entities, dict):
        return {}
    return entities
