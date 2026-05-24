from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class WorldDataError(ValueError):
    """Raised when world data cannot be loaded or validated."""


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise WorldDataError(f"YAML file does not exist: {path}")

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise WorldDataError(f"Invalid YAML in {path}: {exc}") from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise WorldDataError(f"YAML file must contain a mapping: {path}")
    return data


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
