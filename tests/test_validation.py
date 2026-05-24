from pathlib import Path

from world_engine.validation import validate_world


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_validate_world_accepts_valid_minimal_world(tmp_path: Path):
    write(tmp_path / "world/world.yaml", "id: world-test\nactive_subject: char-a\n")
    write(
        tmp_path / "world/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: world/chars/a.yaml\n",
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
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: world/chars/a.yaml\n",
    )

    result = validate_world(tmp_path / "world")

    assert "materialized entity char-a path does not exist: world/chars/a.yaml" in result.errors


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


def test_cli_validate_world_reports_ok(tmp_path: Path, capsys):
    from world_engine.cli import main

    write(tmp_path / "world/world.yaml", "id: world-test\nactive_subject: char-a\n")
    write(
        tmp_path / "world/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: world/chars/a.yaml\n",
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
