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


@dataclass(frozen=True)
class HarvestContext:
    corpse_not_burned: bool
    harvested_within_hours: int
    extraction_skill: str


@dataclass(frozen=True)
class MaterialHarvestResult:
    obtained_material_ids: list[str]
    failed_material_ids: list[str]


def calculate_material_harvest(
    beast_template: dict[str, Any],
    *,
    beast_layer: int,
    context: HarvestContext,
    rolls: dict[str, float],
) -> MaterialHarvestResult:
    obtained: list[str] = []
    failed: list[str] = []
    materials = beast_template.get("materials", [])
    if not isinstance(materials, list):
        return MaterialHarvestResult(obtained_material_ids=[], failed_material_ids=[])

    for material in materials:
        if not isinstance(material, dict):
            continue
        material_id = material["id"]
        chance = float(material["chance"])
        roll = rolls.get(material_id)
        if roll is None:
            raise ValueError(f"missing harvest roll for material: {material_id}")

        if _requirements_met(material.get("condition_requirements", {}), beast_layer, context) and roll <= chance:
            obtained.append(material_id)
        else:
            failed.append(material_id)

    return MaterialHarvestResult(obtained_material_ids=obtained, failed_material_ids=failed)


def _requirements_met(
    requirements: object,
    beast_layer: int,
    context: HarvestContext,
) -> bool:
    if not isinstance(requirements, dict):
        return True

    if requirements.get("corpse_not_burned") is True and not context.corpse_not_burned:
        return False

    harvested_limit = requirements.get("harvested_within_hours")
    if isinstance(harvested_limit, int) and context.harvested_within_hours > harvested_limit:
        return False

    layer_min = requirements.get("layer_min")
    if isinstance(layer_min, int) and beast_layer < layer_min:
        return False

    return True
