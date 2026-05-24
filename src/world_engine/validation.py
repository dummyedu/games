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
    content_by_id: dict[str, dict[str, object]] = {}
    spiritual_root_ids: set[str] | None = None
    action_types: set[str] | None = None
    authority_ranks: set[str] | None = None
    if ruleset:
        root = rulesets_root or _default_rulesets_root(world_root)
        ruleset_path = root / str(ruleset)
        if not ruleset_path.exists():
            errors.append(f"ruleset {ruleset} does not exist")
        else:
            content_by_id = _collect_content_by_id(ruleset_path)
            content_ids = set(content_by_id)
            spiritual_root_ids = _collect_spiritual_root_ids(ruleset_path)
            action_types, authority_ranks = _collect_action_rule_ids(ruleset_path)

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
            _validate_entity_ruleset_references(
                entity_id,
                entity,
                entity_data,
                content_ids,
                content_by_id,
                spiritual_root_ids,
                entities,
                action_types,
                authority_ranks,
                errors,
            )
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
    return set(_collect_content_by_id(ruleset_path))


def _collect_content_by_id(ruleset_path: Path) -> dict[str, dict[str, object]]:
    content_root = ruleset_path / "content"
    if not content_root.exists():
        return {}

    content_by_id: dict[str, dict[str, object]] = {}
    for path in content_root.rglob("*.yaml"):
        try:
            data = load_yaml(path)
        except WorldDataError:
            continue
        content_id = data.get("id")
        if isinstance(content_id, str):
            content_by_id[content_id] = data
    return content_by_id


def _collect_spiritual_root_ids(ruleset_path: Path) -> set[str]:
    path = ruleset_path / "cultivation.yaml"
    if not path.exists():
        return set()

    try:
        data = load_yaml(path)
    except WorldDataError:
        return set()

    roots = data.get("spiritual_roots", {})
    if isinstance(roots, dict):
        return {root_id for root_id in roots if isinstance(root_id, str)}
    return set()


def _collect_action_rule_ids(ruleset_path: Path) -> tuple[set[str], set[str]]:
    path = ruleset_path / "actions.yaml"
    if not path.exists():
        return set(), set()

    try:
        data = load_yaml(path)
    except WorldDataError:
        return set(), set()

    action_types = data.get("action_types", [])
    authority_ranks = data.get("authority_ranks", [])
    return _string_set(action_types), _string_set(authority_ranks)


def _string_set(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


def _validate_entity_ruleset_references(
    entity_id: str,
    entity_index: dict[str, object],
    entity_data: dict[str, object],
    content_ids: set[str] | None,
    content_by_id: dict[str, dict[str, object]],
    spiritual_root_ids: set[str] | None,
    entities: dict[str, dict[str, object]],
    action_types: set[str] | None,
    authority_ranks: set[str] | None,
    errors: list[str],
) -> None:
    entity_type = entity_index.get("type")
    if entity_type == "character":
        true_state = entity_data.get("true_state", {})
        if isinstance(true_state, dict) and spiritual_root_ids is not None:
            spiritual_root = true_state.get("spiritual_root")
            if isinstance(spiritual_root, str) and spiritual_root not in spiritual_root_ids:
                errors.append(
                    f"character {entity_id} references missing spiritual root: {spiritual_root}"
                )

        if content_ids is None:
            return

        skills = entity_data.get("skills", {})
        if isinstance(skills, dict):
            for content_id in skills:
                if content_id not in content_ids:
                    errors.append(f"character {entity_id} references missing content id: {content_id}")
                    continue
                _validate_spell_element(entity_id, str(content_id), content_by_id, true_state, errors)

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
        if content_ids is None:
            return

        inventory = entity_data.get("inventory", {})
        if isinstance(inventory, dict):
            for content_id in inventory:
                if content_id not in content_ids:
                    errors.append(f"facility {entity_id} references missing content id: {content_id}")

    _validate_action_rules(
        entity_id,
        entity_data,
        entities,
        action_types,
        authority_ranks,
        errors,
    )


def _validate_action_rules(
    entity_id: str,
    entity_data: dict[str, object],
    entities: dict[str, dict[str, object]],
    action_types: set[str] | None,
    authority_ranks: set[str] | None,
    errors: list[str],
) -> None:
    action_rules = entity_data.get("action_rules", {})
    if not isinstance(action_rules, dict):
        return

    for rule_id, rule in action_rules.items():
        if not isinstance(rule_id, str) or not isinstance(rule, dict):
            continue

        rule_type = rule.get("type")
        if (
            action_types is not None
            and isinstance(rule_type, str)
            and rule_type not in action_types
        ):
            errors.append(
                f"entity {entity_id} action rule {rule_id} references unknown action type: {rule_type}"
            )

        minimum_rank = rule.get("minimum_rank")
        if (
            authority_ranks is not None
            and isinstance(minimum_rank, str)
            and minimum_rank not in authority_ranks
        ):
            errors.append(
                f"entity {entity_id} action rule {rule_id} references unknown authority rank: {minimum_rank}"
            )

        target = rule.get("target")
        if isinstance(target, str) and target not in entities:
            errors.append(
                f"entity {entity_id} action rule {rule_id} references unknown target: {target}"
            )


def _validate_spell_element(
    entity_id: str,
    content_id: str,
    content_by_id: dict[str, dict[str, object]],
    true_state: dict[object, object],
    errors: list[str],
) -> None:
    content = content_by_id.get(content_id, {})
    if content.get("type") != "attack" and "element" not in content:
        return

    element = content.get("element")
    if not isinstance(element, str) or element in {"neutral", "none"}:
        return

    root_elements = true_state.get("root_elements", [])
    if not isinstance(root_elements, list):
        root_elements = []
    allowed = {item for item in root_elements if isinstance(item, str)}
    if element in allowed:
        return

    allowed_text = ", ".join(sorted(allowed)) if allowed else "none"
    errors.append(
        f"character {entity_id} cannot use spell {content_id} with element {element} "
        f"outside root elements: {allowed_text}"
    )
