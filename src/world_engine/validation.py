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
    content_ids: set[str] | None = None
    if ruleset:
        root = rulesets_root or _default_rulesets_root(world_root)
        ruleset_path = root / str(ruleset)
        if not ruleset_path.exists():
            errors.append(f"ruleset {ruleset} does not exist")
        else:
            content_ids = _collect_content_ids(ruleset_path)

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
            if not world_relative_path.exists():
                errors.append(f"materialized entity {entity_id} path does not exist: {path_value}")
                continue

            try:
                entity_data = load_yaml(world_relative_path)
            except WorldDataError as exc:
                errors.append(str(exc))
                continue

            file_id = entity_data.get("id")
            if file_id != entity_id:
                errors.append(f"materialized entity {entity_id} file id mismatch: {file_id}")
            _validate_entity_content_references(entity_id, entity, entity_data, content_ids, errors)
        elif state == "indexed":
            if path_value is not None:
                warnings.append(f"indexed entity {entity_id} has path {path_value}")
        else:
            errors.append(f"entity {entity_id} has unsupported state: {state}")

    return ValidationResult(errors=errors, warnings=warnings)


def _default_rulesets_root(world_root: Path) -> Path:
    if world_root.parent.name == "worlds":
        return world_root.parent.parent / "rulesets"
    return world_root.parent / "rulesets"


def _collect_content_ids(ruleset_path: Path) -> set[str]:
    content_root = ruleset_path / "content"
    if not content_root.exists():
        return set()

    content_ids: set[str] = set()
    for path in content_root.rglob("*.yaml"):
        try:
            data = load_yaml(path)
        except WorldDataError:
            continue
        content_id = data.get("id")
        if isinstance(content_id, str):
            content_ids.add(content_id)
    return content_ids


def _validate_entity_content_references(
    entity_id: str,
    entity_index: dict[str, object],
    entity_data: dict[str, object],
    content_ids: set[str] | None,
    errors: list[str],
) -> None:
    if content_ids is None:
        return

    entity_type = entity_index.get("type")
    if entity_type == "character":
        skills = entity_data.get("skills", {})
        if isinstance(skills, dict):
            for content_id in skills:
                if content_id not in content_ids:
                    errors.append(f"character {entity_id} references missing content id: {content_id}")

        equipment = entity_data.get("equipment", [])
        if isinstance(equipment, list):
            for content_id in equipment:
                if isinstance(content_id, str) and content_id not in content_ids:
                    errors.append(f"character {entity_id} references missing content id: {content_id}")

        resources = entity_data.get("resources", {})
        if isinstance(resources, dict):
            consumables = resources.get("consumables", [])
            if isinstance(consumables, list):
                for content_id in consumables:
                    if isinstance(content_id, str) and content_id not in content_ids:
                        errors.append(f"character {entity_id} references missing content id: {content_id}")

    if entity_type == "facility":
        inventory = entity_data.get("inventory", {})
        if isinstance(inventory, dict):
            for content_id in inventory:
                if content_id not in content_ids:
                    errors.append(f"facility {entity_id} references missing content id: {content_id}")
