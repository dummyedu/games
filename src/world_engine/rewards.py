from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CombatRewardInput:
    enemy_relative_strength: float
    actual_risk: str
    rounds_survived: int
    meaningful_actions: int
    outcome: str
    repeated_low_risk_count: int
    used_skill_ids: list[str]


@dataclass(frozen=True)
class CombatRewardResult:
    category: str
    combat_experience: int
    skill_sp_multiplier: float
    skill_ids: list[str]


RISK_ORDER = {
    "trivial": 0,
    "low": 1,
    "standard": 2,
    "dangerous": 3,
    "life_threatening": 4,
}


def calculate_combat_reward(
    rules: dict[str, Any],
    reward_input: CombatRewardInput,
) -> CombatRewardResult:
    category = _category_from_relative_strength(rules, reward_input.enemy_relative_strength)
    if RISK_ORDER.get(reward_input.actual_risk, 0) > RISK_ORDER[category]:
        category = reward_input.actual_risk

    anti_farming = rules.get("anti_farming", {})
    repeat_limit = int(anti_farming.get("repeated_low_risk_same_target_limit", 2))
    if (
        reward_input.enemy_relative_strength <= float(rules["relative_strength_thresholds"]["trivial_max"])
        and reward_input.repeated_low_risk_count > repeat_limit
    ):
        category = "trivial"

    reward_categories = rules["reward_categories"]
    reward_data = reward_categories[category]
    return CombatRewardResult(
        category=category,
        combat_experience=int(reward_data["combat_experience"]),
        skill_sp_multiplier=float(reward_data["skill_sp_multiplier"]),
        skill_ids=list(reward_input.used_skill_ids),
    )


def _category_from_relative_strength(rules: dict[str, Any], relative_strength: float) -> str:
    thresholds = rules["relative_strength_thresholds"]
    if relative_strength <= float(thresholds["trivial_max"]):
        return "trivial"
    if relative_strength <= float(thresholds["low_max"]):
        return "low"
    if relative_strength <= float(thresholds["standard_max"]):
        return "standard"
    if relative_strength <= float(thresholds["dangerous_max"]):
        return "dangerous"
    return "life_threatening"
