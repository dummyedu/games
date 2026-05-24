from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from world_engine.ids import load_entity_index
from world_engine.io import WorldDataError, load_yaml


@dataclass(frozen=True)
class ValidationResult:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_world(world_root: Path, rulesets_root: Path | None = None) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        world = load_yaml(world_root / "world.yaml")
    except WorldDataError as exc:
        return ValidationResult(errors=[str(exc)], warnings=[])

    try:
        entities = load_entity_index(world_root)
    except WorldDataError as exc:
        return ValidationResult(errors=[str(exc)], warnings=[])

    active_subject = world.get("active_subject")
    if active_subject and active_subject not in entities:
        errors.append(f"active_subject {active_subject} is not in entity index")

    ruleset = world.get("ruleset")
    if ruleset:
        root = rulesets_root or world_root.parent / "rulesets"
        if not (root / str(ruleset)).exists():
            errors.append(f"ruleset {ruleset} does not exist")

    for entity_id, entity in entities.items():
        if not isinstance(entity, dict):
            errors.append(f"entity {entity_id} must be a mapping")
            continue

        state = entity.get("state")
        path_value = entity.get("path")
        if state == "materialized":
            if not path_value:
                errors.append(f"materialized entity {entity_id} has no path")
                continue
            world_relative_path = world_root / str(path_value)
            legacy_path = world_root.parent / str(path_value)
            if not world_relative_path.exists() and not legacy_path.exists():
                errors.append(f"materialized entity {entity_id} path does not exist: {path_value}")
        elif state == "indexed":
            if path_value is not None:
                warnings.append(f"indexed entity {entity_id} has path {path_value}")
        else:
            errors.append(f"entity {entity_id} has unsupported state: {state}")

    return ValidationResult(errors=errors, warnings=warnings)
