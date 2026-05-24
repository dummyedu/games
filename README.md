# Cultivation World Engine

This repository separates reusable cultivation rules from concrete world saves.

## Layout

```text
rulesets/
  classic_xianxia/      # Shared rules, cultivation physics, content library.
worlds/
  xuanyuan/             # One concrete world save using a ruleset.
src/world_engine/       # Validation and calculation engine.
tests/                  # Regression tests for engine behavior.
```

`rulesets/classic_xianxia/` can be reused by many worlds. A world save declares the ruleset in `world.yaml`:

```yaml
ruleset: classic_xianxia
```

World entity paths in `indexes/entities.yaml` are relative to that world root. For example:

```yaml
char-lin-xuan:
  type: character
  state: materialized
  path: continents/tiannan/materialized/yue/sects/qingyun/characters/lin_xuan.yaml
```

## Validate

Use the project virtual environment:

```bash
.venv/bin/python -m world_engine.cli validate worlds/xuanyuan
```

The validator checks:

- active subject exists in the entity index
- declared ruleset exists
- materialized entity files exist
- materialized file `id` matches the entity id
- character and facility content references exist in the ruleset content library

## Start Another World

Create a new directory under `worlds/`, add `world.yaml`, `indexes/entities.yaml`, and only materialize the places and people the active subject touches. Reuse `ruleset: classic_xianxia` unless the new world needs different cultivation physics or content definitions.
