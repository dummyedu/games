from pathlib import Path

import pytest

from world_engine.io import WorldDataError, load_yaml, write_yaml


def test_load_yaml_returns_mapping(tmp_path: Path):
    path = tmp_path / "sample.yaml"
    path.write_text("id: char-lin-xuan\nname: Lin Xuan\n", encoding="utf-8")

    assert load_yaml(path) == {"id": "char-lin-xuan", "name": "Lin Xuan"}


def test_load_yaml_rejects_missing_file(tmp_path: Path):
    with pytest.raises(WorldDataError, match="YAML file does not exist"):
        load_yaml(tmp_path / "missing.yaml")


def test_load_yaml_rejects_non_mapping(tmp_path: Path):
    path = tmp_path / "list.yaml"
    path.write_text("- one\n- two\n", encoding="utf-8")

    with pytest.raises(WorldDataError, match="must contain a mapping"):
        load_yaml(path)


def test_write_yaml_creates_parent_directory(tmp_path: Path):
    path = tmp_path / "nested" / "state.yaml"

    write_yaml(path, {"id": "event-1", "type": "daily"})

    assert path.exists()
    assert load_yaml(path) == {"id": "event-1", "type": "daily"}
