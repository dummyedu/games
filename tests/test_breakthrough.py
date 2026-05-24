from world_engine.breakthrough import BreakthroughCheck, calculate_success_rate, classify_failure


def test_foundation_success_rate_is_capped():
    check = BreakthroughCheck(
        base_success=20,
        positive_modifiers=[35, 45, 15, 10, 10, 10],
        negative_modifiers=[],
        cap=95,
        floor=5,
    )

    assert calculate_success_rate(check) == 95


def test_forced_breakthrough_keeps_floor():
    check = BreakthroughCheck(
        base_success=20,
        positive_modifiers=[],
        negative_modifiers=[30, 40],
        cap=95,
        floor=5,
    )

    assert calculate_success_rate(check) == 5


def test_classify_failure_band():
    assert classify_failure(success_rate=80, roll=91) == "light"
    assert classify_failure(success_rate=60, roll=95) == "medium"
    assert classify_failure(success_rate=20, roll=90) == "severe"
