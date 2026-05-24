from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from world_engine.io import load_yaml


AUTHOR_PROJECT_MARKERS = (
    "追加一个世界规则",
    "修改世界规则",
    "修改规则",
    "修改项目",
    "改设定",
    "author mode",
    "project mode",
    "change the rules",
    "edit the rules",
    "modify the project",
    "world setup",
)


@dataclass(frozen=True)
class ActionRequest:
    type: str
    actor_id: str
    target_id: str
    declared_intent: str
    current_place: str
    time_sensitivity: str = "normal"
    route: str | None = None
    method: str | None = None
    permission_token: str | None = None
    intermediary: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "type": self.type,
            "actor_id": self.actor_id,
            "target_id": self.target_id,
            "declared_intent": self.declared_intent,
            "current_place": self.current_place,
            "time_sensitivity": self.time_sensitivity,
            "route": self.route,
            "method": self.method,
            "permission_token": self.permission_token,
            "intermediary": self.intermediary,
        }


@dataclass(frozen=True)
class ActionPermissionResult:
    status: str
    reason: str
    cost: dict[str, float | int]
    risk: dict[str, object]
    required_steps: list[str]
    consequences: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "reason": self.reason,
            "cost": dict(self.cost),
            "risk": dict(self.risk),
            "required_steps": list(self.required_steps),
            "consequences": list(self.consequences),
        }


def classify_interaction_mode(user_text: str) -> str:
    normalized = user_text.strip().lower()
    if any(marker in normalized for marker in AUTHOR_PROJECT_MARKERS):
        return "author_project"
    return "player"


def load_action_rules(world_root: Path, rulesets_root: Path | None = None) -> dict[str, Any]:
    world = load_yaml(world_root / "world.yaml")
    ruleset = world.get("ruleset")
    if not isinstance(ruleset, str):
        raise ValueError(f"world has no ruleset: {world_root}")

    root = rulesets_root or _default_rulesets_root(world_root)
    ruleset_rules = load_yaml(root / ruleset / "actions.yaml")
    local_rules = _load_local_action_rules(world_root)
    return {
        "action_types": _as_list(ruleset_rules.get("action_types")),
        "distance_bands": _as_mapping(ruleset_rules.get("distance_bands")),
        "risk_levels": _as_list(ruleset_rules.get("risk_levels")),
        "authority_ranks": _as_list(ruleset_rules.get("authority_ranks")),
        "common_blockers": _as_list(ruleset_rules.get("common_blockers")),
        "outcomes": _as_list(ruleset_rules.get("outcomes")),
        "local_rules": local_rules,
    }


def _default_rulesets_root(world_root: Path) -> Path:
    if world_root.parent.name == "worlds":
        return world_root.parent.parent / "rulesets"
    return world_root.parent / "rulesets"


def _load_local_action_rules(world_root: Path) -> dict[str, dict[str, Any]]:
    local_rules: dict[str, dict[str, Any]] = {}
    for path in world_root.rglob("*.yaml"):
        data = load_yaml(path)
        entity_id = data.get("id")
        action_rules = data.get("action_rules")
        if isinstance(entity_id, str) and isinstance(action_rules, dict):
            local_rules[entity_id] = action_rules
    return local_rules


def _as_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _as_mapping(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {str(key): item for key, item in value.items()}
