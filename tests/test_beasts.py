from pathlib import Path

from world_engine.beasts import load_beast_template


def test_load_firestripe_wolf_template_from_ruleset():
    template = load_beast_template(Path("rulesets/classic_xianxia"), "beast-firestripe-wolf")

    assert template["id"] == "beast-firestripe-wolf"
    assert template["type"] == "beast"
    assert template["variants"]["adult"]["layer_range"] == [2, 4]
    assert template["materials"][0]["id"] == "mat-firestripe-pelt"
