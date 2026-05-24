from pathlib import Path

from world_engine.beasts import generate_beast_instance, load_beast_template


def test_load_firestripe_wolf_template_from_ruleset():
    template = load_beast_template(Path("rulesets/classic_xianxia"), "beast-firestripe-wolf")

    assert template["id"] == "beast-firestripe-wolf"
    assert template["type"] == "beast"
    assert template["variants"]["adult"]["layer_range"] == [2, 4]
    assert template["materials"][0]["id"] == "mat-firestripe-pelt"


def test_generate_adult_firestripe_wolf_instance_with_recorded_rolls():
    template = load_beast_template(Path("rulesets/classic_xianxia"), "beast-firestripe-wolf")

    instance = generate_beast_instance(
        template=template,
        instance_id="beast-firestripe-wolf-test-001",
        variant="adult",
        layer=3,
        location="qinglan-demonwood-forest",
        seed="test-seed-001",
        rolls={
            "life_multiplier": 1.08,
            "mana_multiplier": 1.0,
            "attack_multiplier": 0.96,
            "defense_multiplier": 1.02,
            "speed_multiplier": 1.04,
        },
        growth_state={
            "age_stage": "adult",
            "recent_feeding": "good",
            "spiritual_environment": "low_fire_aspect",
        },
    )

    assert instance["id"] == "beast-firestripe-wolf-test-001"
    assert instance["template"] == "beast-firestripe-wolf"
    assert instance["variant"] == "adult"
    assert instance["layer"] == 3
    assert instance["generation"]["rolls"]["life_multiplier"] == 1.08
    assert instance["combat"]["life"] == 114
    assert instance["combat"]["mana_max"] == 49
    assert instance["combat"]["mana_current"] == 49
    assert instance["combat"]["attack"] == 23
    assert instance["combat"]["defense"] == 12
    assert instance["combat"]["speed"] == 19


def test_generate_beast_instance_rejects_layer_outside_variant_range():
    template = load_beast_template(Path("rulesets/classic_xianxia"), "beast-firestripe-wolf")

    try:
        generate_beast_instance(
            template=template,
            instance_id="bad",
            variant="juvenile",
            layer=4,
            location="qinglan-demonwood-forest",
            seed="test",
            rolls={
                "life_multiplier": 1.0,
                "mana_multiplier": 1.0,
                "attack_multiplier": 1.0,
                "defense_multiplier": 1.0,
                "speed_multiplier": 1.0,
            },
            growth_state={"age_stage": "juvenile"},
        )
    except ValueError as exc:
        assert str(exc) == "layer 4 is outside variant juvenile range: 1-2"
    else:
        raise AssertionError("expected ValueError")
