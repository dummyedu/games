from world_engine.cultivation import CultivationAction, calculate_cp_gain


def test_daily_breathing_uses_talent_environment_and_state():
    action = CultivationAction(
        base_days=10,
        daily_cp=1.0,
        environment_multiplier=1.2,
        state_multiplier=1.0,
        flat_cp=0,
    )

    result = calculate_cp_gain(action)

    assert result.cp_gain == 12
    assert result.days_used == 10
    assert result.side_effects == {}


def test_pill_refinement_adds_flat_cp_and_pill_poison():
    action = CultivationAction(
        base_days=3,
        daily_cp=1.0,
        environment_multiplier=1.0,
        state_multiplier=1.0,
        flat_cp=20,
        side_effects={"pill_poison": 1},
    )

    result = calculate_cp_gain(action)

    assert result.cp_gain == 23
    assert result.side_effects == {"pill_poison": 1}
