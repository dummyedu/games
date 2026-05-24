from world_engine.skills import SkillAction, calculate_sp_gain, stage_for_sp


def test_stage_for_sp_uses_non_linear_thresholds():
    assert stage_for_sp(0) == "unlearned"
    assert stage_for_sp(100) == "entry"
    assert stage_for_sp(400) == "practiced"
    assert stage_for_sp(1200) == "proficient"
    assert stage_for_sp(3200) == "mastered"
    assert stage_for_sp(8200) == "perfected"


def test_high_stage_practice_has_decay():
    action = SkillAction(
        base_sp=10,
        comprehension_multiplier=1.0,
        guidance_multiplier=1.0,
        stage_decay=0.25,
    )

    assert calculate_sp_gain(action) == 2


def test_life_or_death_usage_remains_meaningful():
    action = SkillAction(
        base_sp=120,
        comprehension_multiplier=1.2,
        guidance_multiplier=1.0,
        stage_decay=1.0,
    )

    assert calculate_sp_gain(action) == 144
