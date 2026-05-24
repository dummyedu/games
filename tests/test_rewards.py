from pathlib import Path

from world_engine.io import load_yaml
from world_engine.rewards import CombatRewardInput, calculate_combat_reward


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
