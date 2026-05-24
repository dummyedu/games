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


def resolve_action_permission(
    subject: dict[str, Any],
    action: ActionRequest,
    rules: dict[str, Any],
) -> ActionPermissionResult:
    if action.type == "travel" and action.target_id == "qinglan-herb-market":
        return _resolve_qinglan_market_travel(subject, rules)
    if action.type == "audience" and "ancestor" in action.target_id:
        return _resolve_ancestor_audience(rules)
    if action.type == "speech_claim":
        return ActionPermissionResult(
            status="allowed_with_risk",
            reason="The subject can make the claim, but speech does not alter world truth.",
            cost={"time_days": 0, "spirit_stones_low": 0},
            risk={"level": "medium", "tags": ["false_claim", "sect_law", "reputation"]},
            required_steps=[],
            consequences=[
                "Witnesses may doubt, mock, report, or test the claim.",
                "Law enforcement risk increases if the claim concerns high authority.",
            ],
        )
    return ActionPermissionResult(
        status="impossible_now",
        reason=f"No action permission rule is available for {action.type} targeting {action.target_id}.",
        cost={"time_days": 0, "spirit_stones_low": 0},
        risk={"level": "none", "tags": []},
        required_steps=[],
        consequences=[],
    )


def _resolve_qinglan_market_travel(
    subject: dict[str, Any],
    rules: dict[str, Any],
) -> ActionPermissionResult:
    market_rule = rules["local_rules"]["sect-qingyang"]["market_travel"]
    distance = rules["distance_bands"][market_rule["distance_band"]]
    minimum_rank = str(market_rule.get("minimum_rank", "outer_disciple"))
    current_rank = _subject_authority_rank(subject)
    if not _rank_at_least(current_rank, minimum_rank, rules):
        return ActionPermissionResult(
            status="requires_intermediate",
            reason="The subject must complete outer-disciple registration before making sect-sanctioned market trips.",
            cost={"time_days": 0, "spirit_stones_low": 0},
            risk={"level": "none", "tags": []},
            required_steps=["complete outer-disciple registration at Outer Affairs Hall"],
            consequences=["Attempting to leave before registration may be refused or recorded."],
        )

    tags = list(market_rule.get("risk_tags", []))
    reason = str(market_rule["base_reason"])

    if _is_newly_confirmed_heavenly_root(subject):
        extra = market_rule["extra_risk_if"]["newly_confirmed_heavenly_root"]
        tags.extend(extra.get("tags", []))
        reason = (
            "Outer disciples can make short market trips, but this subject is newly notable "
            "after heavenly fire root confirmation."
        )

    return ActionPermissionResult(
        status=str(market_rule["status"]),
        reason=reason,
        cost={
            "time_days": float(distance["base_time_days"]),
            "spirit_stones_low": 0,
        },
        risk={"level": str(distance["base_risk"]), "tags": tags},
        required_steps=[],
        consequences=[
            "The market can be materialized if the subject goes.",
            "Same-batch candidates or pill-hall contacts may learn of the trip.",
        ],
    )


def _resolve_ancestor_audience(rules: dict[str, Any]) -> ActionPermissionResult:
    rule = rules["local_rules"]["sect-qingyang"]["ancestor_audience"]
    return ActionPermissionResult(
        status=str(rule["status"]),
        reason=str(rule["base_reason"]),
        cost={"time_days": 0, "spirit_stones_low": 0},
        risk={"level": str(rule["risk_level"]), "tags": list(rule["risk_tags"])},
        required_steps=list(rule["required_steps"]),
        consequences=["A crude direct demand may be recorded as arrogance or ignorance."],
    )


def _is_newly_confirmed_heavenly_root(subject: dict[str, Any]) -> bool:
    true_state = subject.get("true_state", {})
    knowledge = subject.get("knowledge", {})
    known_facts = knowledge.get("known_facts", []) if isinstance(knowledge, dict) else []
    return (
        isinstance(true_state, dict)
        and true_state.get("spiritual_root") == "single_element_heavenly_root"
        and any(
            isinstance(fact, str) and "confirmed a single-element heavenly fire root" in fact
            for fact in known_facts
        )
    )


def _subject_authority_rank(subject: dict[str, Any]) -> str:
    identity = subject.get("identity", {})
    if not isinstance(identity, dict):
        return "servant"

    current_status = identity.get("current_status")
    if current_status == "outer_disciple":
        return "outer_disciple"
    if current_status == "inner_disciple":
        return "inner_disciple"
    if current_status == "deacon":
        return "deacon"
    if isinstance(current_status, str) and "servant" in current_status:
        return "servant"
    return "servant"


def _rank_at_least(current_rank: str, minimum_rank: str, rules: dict[str, Any]) -> bool:
    ranks = rules.get("authority_ranks", [])
    if not isinstance(ranks, list):
        return current_rank == minimum_rank
    try:
        return ranks.index(current_rank) >= ranks.index(minimum_rank)
    except ValueError:
        return False
