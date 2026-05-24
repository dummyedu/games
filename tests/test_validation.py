from pathlib import Path

from world_engine.validation import validate_world


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_validate_world_accepts_valid_minimal_world(tmp_path: Path):
    write(tmp_path / "world/world.yaml", "id: world-test\nactive_subject: char-a\n")
    write(
        tmp_path / "world/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: chars/a.yaml\n",
    )
    write(tmp_path / "world/chars/a.yaml", "id: char-a\nname: A\n")

    result = validate_world(tmp_path / "world")

    assert result.errors == []


def test_validate_world_reports_missing_active_subject(tmp_path: Path):
    write(tmp_path / "world/world.yaml", "id: world-test\nactive_subject: char-missing\n")
    write(tmp_path / "world/indexes/entities.yaml", "id: index-entities\nentities: {}\n")

    result = validate_world(tmp_path / "world")

    assert "active_subject char-missing is not in entity index" in result.errors


def test_validate_world_reports_missing_materialized_path(tmp_path: Path):
    write(tmp_path / "world/world.yaml", "id: world-test\nactive_subject: char-a\n")
    write(
        tmp_path / "world/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: chars/a.yaml\n",
    )

    result = validate_world(tmp_path / "world")

    assert "materialized entity char-a path does not exist: chars/a.yaml" in result.errors


def test_validate_world_reports_entity_file_id_mismatch(tmp_path: Path):
    write(tmp_path / "world/world.yaml", "id: world-test\nactive_subject: char-a\n")
    write(
        tmp_path / "world/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: chars/a.yaml\n",
    )
    write(tmp_path / "world/chars/a.yaml", "id: char-b\nname: B\n")

    result = validate_world(tmp_path / "world")

    assert "materialized entity char-a file id mismatch: char-b" in result.errors


def test_validate_world_accepts_external_ruleset_and_world_relative_paths(tmp_path: Path):
    write(
        tmp_path / "rulesets/classic_xianxia/cultivation.yaml",
        "id: rules-cultivation-v1\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/world.yaml",
        "id: world-test\nactive_subject: char-a\nruleset: classic_xianxia\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: chars/a.yaml\n",
    )
    write(tmp_path / "worlds/xuanyuan/chars/a.yaml", "id: char-a\nname: A\n")

    result = validate_world(tmp_path / "worlds/xuanyuan", rulesets_root=tmp_path / "rulesets")

    assert result.errors == []


def test_validate_world_reports_missing_external_ruleset(tmp_path: Path):
    write(
        tmp_path / "worlds/xuanyuan/world.yaml",
        "id: world-test\nactive_subject: char-a\nruleset: missing_rules\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: chars/a.yaml\n",
    )
    write(tmp_path / "worlds/xuanyuan/chars/a.yaml", "id: char-a\nname: A\n")

    result = validate_world(tmp_path / "worlds/xuanyuan", rulesets_root=tmp_path / "rulesets")

    assert "ruleset missing_rules does not exist" in result.errors


def test_validate_world_defaults_rulesets_root_from_worlds_parent(tmp_path: Path):
    write(
        tmp_path / "rulesets/classic_xianxia/cultivation.yaml",
        "id: rules-cultivation-v1\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/world.yaml",
        "id: world-test\nactive_subject: char-a\nruleset: classic_xianxia\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: chars/a.yaml\n",
    )
    write(tmp_path / "worlds/xuanyuan/chars/a.yaml", "id: char-a\nname: A\n")

    result = validate_world(tmp_path / "worlds/xuanyuan")

    assert result.errors == []


def test_validate_world_reports_missing_character_content_references(tmp_path: Path):
    write(
        tmp_path / "rulesets/classic_xianxia/cultivation.yaml",
        "id: rules-cultivation-v1\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/world.yaml",
        "id: world-test\nactive_subject: char-a\nruleset: classic_xianxia\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: chars/a.yaml\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/chars/a.yaml",
        "id: char-a\nname: A\nskills:\n  spell-missing:\n    stage: entry\nequipment:\n  - equip-missing\n",
    )

    result = validate_world(tmp_path / "worlds/xuanyuan")

    assert "character char-a references missing content id: spell-missing" in result.errors
    assert "character char-a references missing content id: equip-missing" in result.errors


def test_validate_world_reports_missing_spiritual_root_definition(tmp_path: Path):
    write(
        tmp_path / "rulesets/classic_xianxia/cultivation.yaml",
        "id: rules-cultivation-v1\nspiritual_roots:\n  five_element_roots:\n    daily_cp: 0.6\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/world.yaml",
        "id: world-test\nactive_subject: char-a\nruleset: classic_xianxia\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: chars/a.yaml\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/chars/a.yaml",
        "id: char-a\nname: A\ntrue_state:\n  spiritual_root: missing_root\n",
    )

    result = validate_world(tmp_path / "worlds/xuanyuan")

    assert "character char-a references missing spiritual root: missing_root" in result.errors


def test_validate_world_reports_spell_outside_character_root_elements(tmp_path: Path):
    write(
        tmp_path / "rulesets/classic_xianxia/cultivation.yaml",
        "id: rules-cultivation-v1\nspiritual_roots:\n  dual_element_roots:\n    daily_cp: 1.2\n",
    )
    write(
        tmp_path / "rulesets/classic_xianxia/content/spells/fireball.yaml",
        "id: spell-fireball-1\ntype: attack\nelement: fire\n",
    )
    write(
        tmp_path / "rulesets/classic_xianxia/content/spells/water_shield.yaml",
        "id: spell-water-shield-1\ntype: defense\nelement: water\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/world.yaml",
        "id: world-test\nactive_subject: char-a\nruleset: classic_xianxia\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: chars/a.yaml\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/chars/a.yaml",
        "id: char-a\nname: A\ntrue_state:\n  spiritual_root: dual_element_roots\n  root_elements:\n    - water\nskills:\n  spell-fireball-1:\n    stage: entry\n  spell-water-shield-1:\n    stage: entry\n",
    )

    result = validate_world(tmp_path / "worlds/xuanyuan")

    assert (
        "character char-a cannot use spell spell-fireball-1 with element fire outside root elements: water"
        in result.errors
    )
    assert not any("spell-water-shield-1" in error for error in result.errors)


def test_cli_validate_world_reports_ok(tmp_path: Path, capsys):
    from world_engine.cli import main

    write(tmp_path / "world/world.yaml", "id: world-test\nactive_subject: char-a\n")
    write(
        tmp_path / "world/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: chars/a.yaml\n",
    )
    write(tmp_path / "world/chars/a.yaml", "id: char-a\nname: A\n")

    exit_code = main(["validate", str(tmp_path / "world")])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "valid" in captured.out


def test_cli_validate_world_accepts_rulesets_root(tmp_path: Path, capsys):
    from world_engine.cli import main

    write(
        tmp_path / "rulesets/classic_xianxia/cultivation.yaml",
        "id: rules-cultivation-v1\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/world.yaml",
        "id: world-test\nactive_subject: char-a\nruleset: classic_xianxia\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: chars/a.yaml\n",
    )
    write(tmp_path / "worlds/xuanyuan/chars/a.yaml", "id: char-a\nname: A\n")

    exit_code = main(
        [
            "validate",
            str(tmp_path / "worlds/xuanyuan"),
            "--rulesets-root",
            str(tmp_path / "rulesets"),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "valid" in captured.out


def test_cli_validate_world_defaults_rulesets_root_from_worlds_parent(tmp_path: Path, capsys):
    from world_engine.cli import main

    write(
        tmp_path / "rulesets/classic_xianxia/cultivation.yaml",
        "id: rules-cultivation-v1\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/world.yaml",
        "id: world-test\nactive_subject: char-a\nruleset: classic_xianxia\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: chars/a.yaml\n",
    )
    write(tmp_path / "worlds/xuanyuan/chars/a.yaml", "id: char-a\nname: A\n")

    exit_code = main(["validate", str(tmp_path / "worlds/xuanyuan")])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "valid" in captured.out


def test_repository_seed_worlds_validate():
    assert validate_world(Path("worlds/xuanyuan")).errors == []
    assert validate_world(Path("worlds/qinglan_frontier")).errors == []


def test_validate_world_reports_unknown_local_action_type(tmp_path: Path):
    write(
        tmp_path / "rulesets/classic_xianxia/actions.yaml",
        "id: rules-actions-v1\naction_types:\n  - travel\nrisk_levels:\n  - low\nauthority_ranks:\n  - outer_disciple\n",
    )
    write(
        tmp_path / "rulesets/classic_xianxia/cultivation.yaml",
        "id: rules-cultivation-v1\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/world.yaml",
        "id: world-test\nactive_subject: char-a\nruleset: classic_xianxia\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: chars/a.yaml\n  sect-a:\n    type: sect\n    state: materialized\n    path: sects/a.yaml\n",
    )
    write(tmp_path / "worlds/xuanyuan/chars/a.yaml", "id: char-a\nname: A\n")
    write(
        tmp_path / "worlds/xuanyuan/sects/a.yaml",
        "id: sect-a\naction_rules:\n  bad_rule:\n    type: forbidden_teleport\n",
    )

    result = validate_world(tmp_path / "worlds/xuanyuan")

    assert "entity sect-a action rule bad_rule references unknown action type: forbidden_teleport" in result.errors


def test_validate_world_reports_unknown_local_rank_and_target(tmp_path: Path):
    write(
        tmp_path / "rulesets/classic_xianxia/actions.yaml",
        "id: rules-actions-v1\naction_types:\n  - travel\nrisk_levels:\n  - low\nauthority_ranks:\n  - outer_disciple\n",
    )
    write(
        tmp_path / "rulesets/classic_xianxia/cultivation.yaml",
        "id: rules-cultivation-v1\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/world.yaml",
        "id: world-test\nactive_subject: char-a\nruleset: classic_xianxia\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: chars/a.yaml\n  sect-a:\n    type: sect\n    state: materialized\n    path: sects/a.yaml\n",
    )
    write(tmp_path / "worlds/xuanyuan/chars/a.yaml", "id: char-a\nname: A\n")
    write(
        tmp_path / "worlds/xuanyuan/sects/a.yaml",
        "id: sect-a\naction_rules:\n  market:\n    type: travel\n    target: missing-market\n    minimum_rank: core_disciple\n",
    )

    result = validate_world(tmp_path / "worlds/xuanyuan")

    assert "entity sect-a action rule market references unknown authority rank: core_disciple" in result.errors
    assert "entity sect-a action rule market references unknown target: missing-market" in result.errors
