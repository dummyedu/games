from pathlib import Path

from world_engine.beasts import load_beast_template
from world_engine.io import load_yaml
from world_engine.rewards import (
    CombatRewardInput,
    HarvestContext,
    calculate_combat_reward,
    calculate_material_harvest,
)


def test_calculate_standard_combat_reward():
    rules = load_yaml(Path("rulesets/classic_xianxia/combat_rewards.yaml"))
    result = calculate_combat_reward(
        rules,
        CombatRewardInput(
            enemy_relative_strength=1.0,
            actual_risk="standard",
            rounds_survived=3,
            meaningful_actions=2,
            outcome="victory",
            repeated_low_risk_count=0,
            used_skill_ids=["spell-fireball-1"],
        ),
    )

    assert result.category == "standard"
    assert result.combat_experience == 2
    assert result.skill_sp_multiplier == 1.0
    assert result.skill_ids == ["spell-fireball-1"]


def test_repeated_trivial_fight_awards_no_combat_experience():
    rules = load_yaml(Path("rulesets/classic_xianxia/combat_rewards.yaml"))
    result = calculate_combat_reward(
        rules,
        CombatRewardInput(
            enemy_relative_strength=0.2,
            actual_risk="low",
            rounds_survived=1,
            meaningful_actions=1,
            outcome="victory",
            repeated_low_risk_count=5,
            used_skill_ids=["spell-fireball-1"],
        ),
    )

    assert result.category == "trivial"
    assert result.combat_experience == 0
    assert result.skill_sp_multiplier == 0.1


def test_calculate_material_harvest_respects_rolls_and_conditions():
    template = load_beast_template(Path("rulesets/classic_xianxia"), "beast-firestripe-wolf")

    result = calculate_material_harvest(
        template,
        beast_layer=3,
        context=HarvestContext(
            corpse_not_burned=True,
            harvested_within_hours=1,
            extraction_skill="basic",
        ),
        rolls={
            "mat-firestripe-pelt": 0.4,
            "mat-warm-beast-blood": 0.5,
            "mat-beast-core-fragment": 0.1,
        },
    )

    assert result.obtained_material_ids == [
        "mat-firestripe-pelt",
        "mat-warm-beast-blood",
        "mat-beast-core-fragment",
    ]
    assert result.failed_material_ids == []


def test_calculate_material_harvest_blocks_burned_pelt_and_late_blood():
    template = load_beast_template(Path("rulesets/classic_xianxia"), "beast-firestripe-wolf")

    result = calculate_material_harvest(
        template,
        beast_layer=3,
        context=HarvestContext(
            corpse_not_burned=False,
            harvested_within_hours=4,
            extraction_skill="basic",
        ),
        rolls={
            "mat-firestripe-pelt": 0.1,
            "mat-warm-beast-blood": 0.1,
            "mat-beast-core-fragment": 0.9,
        },
    )

    assert result.obtained_material_ids == []
    assert result.failed_material_ids == [
        "mat-firestripe-pelt",
        "mat-warm-beast-blood",
        "mat-beast-core-fragment",
    ]
