# AGENTS.md

## Project

This is a Python 3.12+ cultivation world engine. Reusable rules live in `rulesets/`, concrete world saves live in `worlds/`, and engine code lives in `src/world_engine/`.

## Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Verify

```bash
. .venv/bin/activate
python -m pytest
python -m world_engine.cli validate worlds/xuanyuan
python -m world_engine.cli validate worlds/qinglan_frontier
```

## Editing Rules

- Keep reusable mechanics and content definitions under `rulesets/`.
- Keep concrete world state under `worlds/`.
- Prefer focused tests for engine behavior changes.
- Do not rewrite unrelated YAML world data.
- Preserve existing world IDs and index paths unless a task explicitly asks to change them.
