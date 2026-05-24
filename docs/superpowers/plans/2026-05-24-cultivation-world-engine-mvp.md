# Cultivation World Engine MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first testable version of the cultivation world engine: YAML world files, schema validation, cultivation/breakthrough/skill calculators, a small content library, and an objective combat resolver.

**Architecture:** Implement a small Python package named `world_engine` with pure calculation modules and file-system adapters. World state and rules live in YAML files under `world/`; scripts and CLI commands read those files, calculate objective outcomes, and return structured results that the LLM can use when writing events.

**Tech Stack:** Python 3.12+, PyYAML, pytest, standard-library `argparse`, dataclasses, pathlib.

---

## Post-MVP Layout Update

This plan was executed when the seed world still used a single `world/` directory. The current repository has since separated reusable rules from world saves:

```text
rulesets/classic_xianxia/
worlds/xuanyuan/
```

For current work, use `README.md` and `docs/superpowers/specs/2026-05-24-cultivation-world-engine-design.md` as the source of truth for paths. The older `world/...` paths below are retained as execution history for the original MVP plan.

The current ruleset also uses an element-root model (`five_element_roots`, `single_element_heavenly_root`, `mutated_root`, etc.) rather than the original MVP's generic poor/middle/superior root ladder.

---

## Scope Boundary

This plan implements the first playable engine foundation from the approved spec at `docs/superpowers/specs/2026-05-24-cultivation-world-engine-design.md`.

Included:

- Project scaffold and tests.
- YAML loading and writing.
- Reference validation for entities, characters, content, and events.
- Seed outer-sect world files.
- Minimal content rule library.
- Cultivation CP calculator.
- Breakthrough success calculator.
- Skill SP calculator.
- Round-based combat resolver.
- CLI wrappers for validation and calculators.

Excluded from this first plan:

- LLM orchestration.
- UI.
- Procedural full-world generation.
- Long-term return-progression generation.
- Large content library beyond the outer-sect starter set.

## File Map

- Create: `pyproject.toml` - package metadata and test dependencies.
- Create: `src/world_engine/__init__.py` - package marker and version.
- Create: `src/world_engine/io.py` - YAML read/write helpers.
- Create: `src/world_engine/ids.py` - reference collection helpers.
- Create: `src/world_engine/validation.py` - world and content validation.
- Create: `src/world_engine/cultivation.py` - CP calculation.
- Create: `src/world_engine/breakthrough.py` - large-realm success calculation.
- Create: `src/world_engine/skills.py` - SP stage calculation.
- Create: `src/world_engine/combat.py` - round combat resolver.
- Create: `src/world_engine/cli.py` - command line entry point.
- Create: `tests/test_io.py`
- Create: `tests/test_validation.py`
- Create: `tests/test_cultivation.py`
- Create: `tests/test_breakthrough.py`
- Create: `tests/test_skills.py`
- Create: `tests/test_combat.py`
- Create: `world/world.yaml`
- Create: `world/rules/cultivation.yaml`
- Create: `world/rules/breakthroughs.yaml`
- Create: `world/rules/content/spells/fireball.yaml`
- Create: `world/rules/content/spells/water_shield.yaml`
- Create: `world/rules/content/spells/wind_step.yaml`
- Create: `world/rules/content/equipment/low_grade_flying_sword.yaml`
- Create: `world/rules/content/equipment/ironwood_shield.yaml`
- Create: `world/rules/content/consumables/ordinary_qi_gathering_pill.yaml`
- Create: `world/rules/content/status_effects/light_wound.yaml`
- Create: `world/rules/content/status_effects/mana_exhaustion.yaml`
- Create: `world/indexes/entities.yaml`
- Create: `world/indexes/unresolved_hooks.yaml`
- Create: `world/continents/tiannan/continent.yaml`
- Create: `world/continents/tiannan/known_entities.yaml`
- Create: `world/continents/tiannan/materialized/yue/sects/qingyun/sect.yaml`
- Create: `world/continents/tiannan/materialized/yue/sects/qingyun/characters/lin_xuan.yaml`
- Create: `world/continents/tiannan/materialized/yue/sects/qingyun/characters/zhao_shi.yaml`
- Create: `world/continents/tiannan/materialized/yue/sects/qingyun/facilities/pill_hall.yaml`
- Create: `world/continents/tiannan/materialized/yue/sects/qingyun/relationships/outer_room_c3.yaml`

---

### Task 1: Project Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `src/world_engine/__init__.py`

- [ ] **Step 1: Create package metadata**

Write `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "cultivation-world-engine"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["PyYAML>=6.0.1"]

[project.optional-dependencies]
dev = ["pytest>=8.2"]

[project.scripts]
world-engine = "world_engine.cli:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 2: Create package marker**

Write `src/world_engine/__init__.py`:

```python
"""Persistent cultivation world engine."""

__version__ = "0.1.0"
```

- [ ] **Step 3: Install package in editable mode**

Run:

```bash
python -m pip install -e ".[dev]"
```

Expected: command exits with code 0 and installs `PyYAML` and `pytest`.

- [ ] **Step 4: Run empty test suite**

Run:

```bash
python -m pytest -q
```

Expected: pytest exits with code 5 because no tests exist yet.

- [ ] **Step 5: Commit**

If the workspace is a git repository, run:

```bash
git add pyproject.toml src/world_engine/__init__.py
git commit -m "chore: scaffold cultivation world engine"
```

Expected: commit succeeds. If the workspace is not a git repository, record this fact in the implementation notes and continue.

---

### Task 2: YAML IO Helpers

**Files:**
- Create: `src/world_engine/io.py`
- Test: `tests/test_io.py`

- [ ] **Step 1: Write failing IO tests**

Write `tests/test_io.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m pytest tests/test_io.py -q
```

Expected: FAIL with `ModuleNotFoundError` or import error for `world_engine.io`.

- [ ] **Step 3: Implement IO helpers**

Write `src/world_engine/io.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class WorldDataError(ValueError):
    """Raised when world data cannot be loaded or validated."""


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise WorldDataError(f"YAML file does not exist: {path}")

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise WorldDataError(f"Invalid YAML in {path}: {exc}") from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise WorldDataError(f"YAML file must contain a mapping: {path}")
    return data


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
```

- [ ] **Step 4: Run IO tests**

Run:

```bash
python -m pytest tests/test_io.py -q
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

If git is available:

```bash
git add src/world_engine/io.py tests/test_io.py
git commit -m "feat: add yaml world io helpers"
```

---

### Task 3: Seed Rule And World Files

**Files:**
- Create the world YAML files listed in the File Map under `world/`.

- [ ] **Step 1: Create global world file**

Write `world/world.yaml`:

```yaml
id: world-xuanyuan
name: Xuanyuan Realm
current_time:
  calendar: Xuanyuan
  year: 102
  season: spring
  month: 3
  day: 7
active_subject: char-lin-xuan
focus:
  continent: cont-tiannan
  region: yue-cultivation-region
  place: sect-qingyun-outer
principles:
  - claims_are_not_facts
  - actions_change_truth
  - subject_increases_event_resolution
```

- [ ] **Step 2: Create cultivation rules**

Write `world/rules/cultivation.yaml`:

```yaml
id: rules-cultivation-v1
talents:
  poor_spiritual_root:
    daily_cp: 0.5
  middle_spiritual_root:
    daily_cp: 1.0
  superior_spiritual_root:
    daily_cp: 1.5
  excellent_spiritual_root:
    daily_cp: 2.0
  heavenly_spiritual_root:
    daily_cp: 3.0
qi_refining_thresholds:
  layer_1_to_2: 120
  layer_2_to_3: 240
  layer_3_to_4: 480
  layer_4_to_5: 900
  layer_5_to_6: 1400
  layer_6_to_7: 2200
  layer_7_to_8: 3300
  layer_8_to_9: 5000
  layer_9_to_perfection: 4000
cultivation_states:
  not_cultivating:
    monthly_cp_min: 0
    monthly_cp_max: 0
  occasional:
    monthly_cp_min: 1
    monthly_cp_max: 10
  stable:
    monthly_cp_min: 20
    monthly_cp_max: 60
  key_target:
    monthly_cp_min: 60
    monthly_cp_max: 150
```

- [ ] **Step 3: Create breakthrough rules**

Write `world/rules/breakthroughs.yaml`:

```yaml
id: rules-breakthroughs-v1
foundation_establishment:
  base_success: 20
  cap: 95
  floor: 5
  modifiers:
    foundation_pill: 35
    superior_foundation_pill: 45
    spiritual_site_low: 5
    spiritual_site_good: 15
    complete_matching_technique: 10
    solid_foundation: 10
    stable_mind: 10
    elder_protection: 10
    visible_pill_poison: -20
    hidden_wound: -20
    severe_wound: -40
    old_age_pressure: -10
    forced_breakthrough: -30
failure_bands:
  light:
    over_by_min: 1
    over_by_max: 20
  medium:
    over_by_min: 21
    over_by_max: 50
  severe:
    over_by_min: 51
    over_by_max: 100
```

- [ ] **Step 4: Create content files**

Write `world/rules/content/spells/fireball.yaml`:

```yaml
id: spell-fireball-1
name: Fireball
grade: first_rank_lower
type: attack
element: fire
mana_cost: 12
cast_speed: 2
base_hit: 70
effect:
  damage_type: fire
  base_damage: 30
  penetration: 0
proficiency_modifiers:
  entry:
    damage_multiplier: 0.8
    hit_modifier: -10
  practiced:
    damage_multiplier: 1.0
    hit_modifier: 0
  proficient:
    damage_multiplier: 1.15
    mana_cost_multiplier: 0.9
  mastered:
    damage_multiplier: 1.3
    cast_speed_modifier: 1
```

Write `world/rules/content/spells/water_shield.yaml`:

```yaml
id: spell-water-shield-1
name: Water Shield
grade: first_rank_lower
type: defense
element: water
mana_cost: 10
cast_speed: 2
base_hit: 100
effect:
  shield: 24
  duration_rounds: 1
proficiency_modifiers:
  entry:
    shield_multiplier: 0.8
  practiced:
    shield_multiplier: 1.0
  proficient:
    shield_multiplier: 1.15
    mana_cost_multiplier: 0.9
  mastered:
    shield_multiplier: 1.3
```

Write `world/rules/content/spells/wind_step.yaml`:

```yaml
id: spell-wind-step-1
name: Wind Step
grade: first_rank_lower
type: movement
element: wind
mana_cost: 8
cast_speed: 1
base_hit: 100
effect:
  speed_bonus: 15
  dodge_bonus: 10
  duration_rounds: 1
proficiency_modifiers:
  entry:
    speed_multiplier: 0.8
  practiced:
    speed_multiplier: 1.0
  proficient:
    speed_multiplier: 1.15
    mana_cost_multiplier: 0.9
  mastered:
    speed_multiplier: 1.3
```

Write `world/rules/content/equipment/low_grade_flying_sword.yaml`:

```yaml
id: equip-low-grade-flying-sword
name: Low-grade Flying Sword
grade: low_grade_artifact
slot: weapon
bonuses:
  attack: 18
  speed: 3
traits:
  melee_penetration: 5
```

Write `world/rules/content/equipment/ironwood_shield.yaml`:

```yaml
id: equip-ironwood-shield
name: Ironwood Shield
grade: low_grade_artifact
slot: offhand
bonuses:
  defense: 12
traits:
  active_shield: 25
  mana_cost: 5
```

Write `world/rules/content/consumables/ordinary_qi_gathering_pill.yaml`:

```yaml
id: cons-ordinary-qi-gathering-pill
name: Ordinary Qi Gathering Pill
type: pill
effects:
  cp: 20
  refine_days: 3
side_effects:
  pill_poison: 1
limits:
  repeat_window_days: 10
```

Write `world/rules/content/status_effects/light_wound.yaml`:

```yaml
id: status-light-wound
name: Light Wound
type: injury
modifiers:
  attack_multiplier: 0.95
  speed_multiplier: 0.95
```

Write `world/rules/content/status_effects/mana_exhaustion.yaml`:

```yaml
id: status-mana-exhaustion
name: Mana Exhaustion
type: resource_state
modifiers:
  attack_multiplier: 0.7
  speed_multiplier: 0.8
```

- [ ] **Step 5: Create starter world files**

Write `world/indexes/entities.yaml`:

```yaml
id: index-entities
entities:
  char-lin-xuan:
    type: character
    state: materialized
    path: world/continents/tiannan/materialized/yue/sects/qingyun/characters/lin_xuan.yaml
  char-zhao-shi:
    type: character
    state: materialized
    path: world/continents/tiannan/materialized/yue/sects/qingyun/characters/zhao_shi.yaml
  sect-qingyun:
    type: sect
    state: materialized
    path: world/continents/tiannan/materialized/yue/sects/qingyun/sect.yaml
  facility-qingyun-pill-hall:
    type: facility
    state: materialized
    path: world/continents/tiannan/materialized/yue/sects/qingyun/facilities/pill_hall.yaml
  magic-six-sects:
    type: alliance
    state: indexed
    path: null
```

Write `world/indexes/unresolved_hooks.yaml`:

```yaml
id: index-unresolved-hooks
hooks: []
```

Write `world/continents/tiannan/continent.yaml`:

```yaml
id: cont-tiannan
name: Tiannan Continent
state: partially_indexed
known_patterns:
  - orthodox_sects
  - demonic_sects
  - scattered_cultivator_markets
```

Write `world/continents/tiannan/known_entities.yaml`:

```yaml
id: tiannan-known-entities
indexed_entities:
  - id: yue-cultivation-region
    type: region
    description: Local cultivation region around Yue.
  - id: magic-six-sects
    type: alliance
    description: Indexed but not materialized demonic alliance.
```

Write `world/continents/tiannan/materialized/yue/sects/qingyun/sect.yaml`:

```yaml
id: sect-qingyun
name: Qingyun Sect
type: sect
state: materialized
rank: foundation_establishment_sect
facilities:
  - facility-qingyun-pill-hall
characters:
  - char-lin-xuan
  - char-zhao-shi
rules:
  outer_disciple_monthly_allowance:
    ordinary_qi_gathering_pill: 1
```

Write `world/continents/tiannan/materialized/yue/sects/qingyun/characters/lin_xuan.yaml`:

```yaml
id: char-lin-xuan
name: Lin Xuan
state: active_subject
true_state:
  realm: qi_refining
  layer: 3
  cp: 430
  current_layer_cp_required: 480
  spiritual_root: middle_spiritual_root
  age: 17
  lifespan_limit: 120
  foundation: ordinary
  pill_poison: 0
  wounds: []
cultivation_state:
  rhythm: stable
  bottleneck: null
combat:
  mana_max: 120
  mana_current: 120
  life: 100
  divine_sense: 20
  attack: 35
  defense: 20
  speed: 25
  control_resistance: 10
  poison_resistance: 5
  combat_experience: 12
skills:
  spell-fireball-1:
    source: Qingyun library
    completeness: complete
    stage: practiced
    sp: 420
equipment:
  - equip-low-grade-flying-sword
resources:
  spirit_stones_low: 23
  consumables: []
knowledge:
  known_facts:
    - Qingyun outer disciples can receive one ordinary qi gathering pill per month.
  rumors: []
relationships:
  char-zhao-shi:
    type: roommate
    trust: 35
    belief: Honest but timid.
event_history: []
```

Write `world/continents/tiannan/materialized/yue/sects/qingyun/characters/zhao_shi.yaml`:

```yaml
id: char-zhao-shi
name: Zhao Shi
state: standard_character
true_state:
  realm: qi_refining
  layer: 2
  cp: 160
  current_layer_cp_required: 240
  spiritual_root: poor_spiritual_root
  age: 19
  lifespan_limit: 110
  foundation: ordinary
  pill_poison: 0
  wounds: []
cultivation_state:
  rhythm: occasional
  bottleneck: resources
combat:
  mana_max: 85
  mana_current: 85
  life: 100
  divine_sense: 12
  attack: 22
  defense: 15
  speed: 18
  control_resistance: 6
  poison_resistance: 4
  combat_experience: 4
skills: {}
equipment: []
resources:
  spirit_stones_low: 4
  consumables: []
knowledge:
  known_facts: []
  rumors: []
relationships:
  char-lin-xuan:
    type: roommate
    trust: 55
    belief: Quiet but reliable.
event_history: []
```

Write `world/continents/tiannan/materialized/yue/sects/qingyun/facilities/pill_hall.yaml`:

```yaml
id: facility-qingyun-pill-hall
name: Pill Hall
type: facility
state: materialized
owner: sect-qingyun
inventory:
  cons-ordinary-qi-gathering-pill: 120
staff_summary:
  alchemy_apprentices: 12
  delivery_servants: 6
rules:
  - Outer disciples may exchange for one ordinary qi gathering pill per month.
conflicts:
  - Outer disciples suspect allowance skimming.
event_hooks:
  - pill_theft
  - herb_shortage
  - steward_bribe
```

Write `world/continents/tiannan/materialized/yue/sects/qingyun/relationships/outer_room_c3.yaml`:

```yaml
id: relation-scene-qingyun-outer-room-c3
type: residence_relationship_scene
place: sect-qingyun-outer-room-c3
members:
  - char-lin-xuan
  - char-zhao-shi
contact_frequency: high
relationship_network:
  char-lin-xuan__char-zhao-shi:
    surface_relation: roommate
    default_interaction: morning_class_and_evening_room_contact
event_hooks:
  - night_talk_about_outer_rules
  - missing_pill_suspicion
history: []
```

- [ ] **Step 6: Commit**

If git is available:

```bash
git add world
git commit -m "feat: seed starter cultivation world files"
```

---

### Task 4: Reference Collection And Validation

**Files:**
- Create: `src/world_engine/ids.py`
- Create: `src/world_engine/validation.py`
- Test: `tests/test_validation.py`

- [ ] **Step 1: Write failing validation tests**

Write `tests/test_validation.py`:

```python
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
```

- [ ] **Step 2: Run validation tests to verify failure**

Run:

```bash
python -m pytest tests/test_validation.py -q
```

Expected: FAIL because `world_engine.validation` does not exist.

- [ ] **Step 3: Implement reference helper**

Write `src/world_engine/ids.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

from world_engine.io import load_yaml


def load_entity_index(world_root: Path) -> dict[str, dict[str, Any]]:
    path = world_root / "indexes" / "entities.yaml"
    data = load_yaml(path)
    entities = data.get("entities", {})
    if not isinstance(entities, dict):
        return {}
    return entities
```

- [ ] **Step 4: Implement validation**

Write `src/world_engine/validation.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from world_engine.ids import load_entity_index
from world_engine.io import WorldDataError, load_yaml


@dataclass(frozen=True)
class ValidationResult:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_world(world_root: Path) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        world = load_yaml(world_root / "world.yaml")
    except WorldDataError as exc:
        return ValidationResult(errors=[str(exc)], warnings=[])

    try:
        entities = load_entity_index(world_root)
    except WorldDataError as exc:
        return ValidationResult(errors=[str(exc)], warnings=[])

    active_subject = world.get("active_subject")
    if active_subject and active_subject not in entities:
        errors.append(f"active_subject {active_subject} is not in entity index")

    for entity_id, entity in entities.items():
        if not isinstance(entity, dict):
            errors.append(f"entity {entity_id} must be a mapping")
            continue

        state = entity.get("state")
        path_value = entity.get("path")
        if state == "materialized":
            if not path_value:
                errors.append(f"materialized entity {entity_id} has no path")
                continue
            path = world_root.parent / str(path_value)
            if not path.exists():
                errors.append(f"materialized entity {entity_id} path does not exist: {path_value}")
        elif state == "indexed":
            if path_value is not None:
                warnings.append(f"indexed entity {entity_id} has path {path_value}")
        else:
            errors.append(f"entity {entity_id} has unsupported state: {state}")

    return ValidationResult(errors=errors, warnings=warnings)
```

- [ ] **Step 5: Run validation tests**

Run:

```bash
python -m pytest tests/test_validation.py -q
```

Expected: 3 passed.

- [ ] **Step 6: Validate seeded world**

Run:

```bash
python - <<'PY'
from pathlib import Path
from world_engine.validation import validate_world
result = validate_world(Path("world"))
print(result)
raise SystemExit(0 if result.ok else 1)
PY
```

Expected: `ValidationResult(errors=[], warnings=[])` and exit code 0.

- [ ] **Step 7: Commit**

If git is available:

```bash
git add src/world_engine/ids.py src/world_engine/validation.py tests/test_validation.py
git commit -m "feat: validate world entity references"
```

---

### Task 5: Cultivation Calculator

**Files:**
- Create: `src/world_engine/cultivation.py`
- Test: `tests/test_cultivation.py`

- [ ] **Step 1: Write failing cultivation tests**

Write `tests/test_cultivation.py`:

```python
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
```

- [ ] **Step 2: Run cultivation tests to verify failure**

Run:

```bash
python -m pytest tests/test_cultivation.py -q
```

Expected: FAIL because `world_engine.cultivation` does not exist.

- [ ] **Step 3: Implement cultivation calculator**

Write `src/world_engine/cultivation.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CultivationAction:
    base_days: int
    daily_cp: float
    environment_multiplier: float
    state_multiplier: float
    flat_cp: int = 0
    side_effects: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class CultivationResult:
    cp_gain: int
    days_used: int
    side_effects: dict[str, int]


def calculate_cp_gain(action: CultivationAction) -> CultivationResult:
    if action.base_days < 0:
        raise ValueError("base_days must be non-negative")
    if action.daily_cp < 0:
        raise ValueError("daily_cp must be non-negative")
    if action.environment_multiplier < 0:
        raise ValueError("environment_multiplier must be non-negative")
    if action.state_multiplier < 0:
        raise ValueError("state_multiplier must be non-negative")

    behavior_cp = action.base_days * action.daily_cp
    scaled_cp = behavior_cp * action.environment_multiplier * action.state_multiplier
    cp_gain = round(scaled_cp + action.flat_cp)
    return CultivationResult(
        cp_gain=cp_gain,
        days_used=action.base_days,
        side_effects=dict(action.side_effects),
    )
```

- [ ] **Step 4: Run cultivation tests**

Run:

```bash
python -m pytest tests/test_cultivation.py -q
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

If git is available:

```bash
git add src/world_engine/cultivation.py tests/test_cultivation.py
git commit -m "feat: calculate cultivation cp gains"
```

---

### Task 6: Breakthrough Calculator

**Files:**
- Create: `src/world_engine/breakthrough.py`
- Test: `tests/test_breakthrough.py`

- [ ] **Step 1: Write failing breakthrough tests**

Write `tests/test_breakthrough.py`:

```python
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
```

- [ ] **Step 2: Run breakthrough tests to verify failure**

Run:

```bash
python -m pytest tests/test_breakthrough.py -q
```

Expected: FAIL because `world_engine.breakthrough` does not exist.

- [ ] **Step 3: Implement breakthrough calculator**

Write `src/world_engine/breakthrough.py`:

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BreakthroughCheck:
    base_success: int
    positive_modifiers: list[int]
    negative_modifiers: list[int]
    cap: int = 95
    floor: int = 5


def calculate_success_rate(check: BreakthroughCheck) -> int:
    raw = check.base_success + sum(check.positive_modifiers) - sum(abs(x) for x in check.negative_modifiers)
    return max(check.floor, min(check.cap, raw))


def classify_failure(success_rate: int, roll: int) -> str:
    if roll <= success_rate:
        return "success"
    over_by = roll - success_rate
    if over_by <= 20:
        return "light"
    if over_by <= 50:
        return "medium"
    return "severe"
```

- [ ] **Step 4: Run breakthrough tests**

Run:

```bash
python -m pytest tests/test_breakthrough.py -q
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

If git is available:

```bash
git add src/world_engine/breakthrough.py tests/test_breakthrough.py
git commit -m "feat: calculate breakthrough success rates"
```

---

### Task 7: Skill SP Calculator

**Files:**
- Create: `src/world_engine/skills.py`
- Test: `tests/test_skills.py`

- [ ] **Step 1: Write failing skill tests**

Write `tests/test_skills.py`:

```python
from world_engine.skills import SkillAction, calculate_sp_gain, stage_for_sp


def test_stage_for_sp_uses_non_linear_thresholds():
    assert stage_for_sp(0) == "unlearned"
    assert stage_for_sp(100) == "entry"
    assert stage_for_sp(400) == "practiced"
    assert stage_for_sp(1200) == "proficient"
    assert stage_for_sp(3200) == "mastered"
    assert stage_for_sp(8200) == "perfected"


def test_high_stage_practice_has_decay():
    action = SkillAction(base_sp=10, comprehension_multiplier=1.0, guidance_multiplier=1.0, stage_decay=0.25)

    assert calculate_sp_gain(action) == 2


def test_life_or_death_usage_remains_meaningful():
    action = SkillAction(base_sp=120, comprehension_multiplier=1.2, guidance_multiplier=1.0, stage_decay=1.0)

    assert calculate_sp_gain(action) == 144
```

- [ ] **Step 2: Run skill tests to verify failure**

Run:

```bash
python -m pytest tests/test_skills.py -q
```

Expected: FAIL because `world_engine.skills` does not exist.

- [ ] **Step 3: Implement skill calculator**

Write `src/world_engine/skills.py`:

```python
from __future__ import annotations

from dataclasses import dataclass


STAGE_THRESHOLDS: tuple[tuple[str, int], ...] = (
    ("perfected", 8200),
    ("mastered", 3200),
    ("proficient", 1200),
    ("practiced", 400),
    ("entry", 100),
    ("unlearned", 0),
)


@dataclass(frozen=True)
class SkillAction:
    base_sp: int
    comprehension_multiplier: float
    guidance_multiplier: float
    stage_decay: float


def stage_for_sp(sp: int) -> str:
    if sp < 0:
        raise ValueError("sp must be non-negative")
    for stage, threshold in STAGE_THRESHOLDS:
        if sp >= threshold:
            return stage
    return "unlearned"


def calculate_sp_gain(action: SkillAction) -> int:
    if action.base_sp < 0:
        raise ValueError("base_sp must be non-negative")
    if action.comprehension_multiplier < 0:
        raise ValueError("comprehension_multiplier must be non-negative")
    if action.guidance_multiplier < 0:
        raise ValueError("guidance_multiplier must be non-negative")
    if action.stage_decay < 0:
        raise ValueError("stage_decay must be non-negative")
    return round(
        action.base_sp
        * action.comprehension_multiplier
        * action.guidance_multiplier
        * action.stage_decay
    )
```

- [ ] **Step 4: Run skill tests**

Run:

```bash
python -m pytest tests/test_skills.py -q
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

If git is available:

```bash
git add src/world_engine/skills.py tests/test_skills.py
git commit -m "feat: calculate skill progression"
```

---

### Task 8: Combat Resolver

**Files:**
- Create: `src/world_engine/combat.py`
- Test: `tests/test_combat.py`

- [ ] **Step 1: Write failing combat tests**

Write `tests/test_combat.py`:

```python
from world_engine.combat import Actor, CombatAction, Spell, resolve_round


def test_attack_spell_hits_and_deals_reduced_damage():
    attacker = Actor(
        id="char-lin-xuan",
        mana=120,
        life=100,
        attack=35,
        defense=20,
        speed=25,
        hit_bonus=0,
        dodge=10,
        shield=0,
    )
    defender = Actor(
        id="char-bandit",
        mana=80,
        life=100,
        attack=25,
        defense=12,
        speed=18,
        hit_bonus=0,
        dodge=5,
        shield=0,
    )
    spell = Spell(
        id="spell-fireball-1",
        kind="attack",
        mana_cost=12,
        base_hit=70,
        base_damage=30,
        hit_modifier=0,
        damage_multiplier=1.0,
        shield=0,
        speed_bonus=0,
        dodge_bonus=0,
    )

    result = resolve_round(
        attacker,
        defender,
        CombatAction(actor_id="char-lin-xuan", spell=spell),
        hit_roll=50,
    )

    assert result.hit is True
    assert result.attacker_mana == 108
    assert result.defender_life == 82
    assert result.injury_state == "normal"


def test_defense_spell_adds_shield_without_damage():
    actor = Actor(
        id="char-lin-xuan",
        mana=120,
        life=100,
        attack=35,
        defense=20,
        speed=25,
        hit_bonus=0,
        dodge=10,
        shield=0,
    )
    defender = Actor(
        id="char-bandit",
        mana=80,
        life=100,
        attack=25,
        defense=12,
        speed=18,
        hit_bonus=0,
        dodge=5,
        shield=0,
    )
    spell = Spell(
        id="spell-water-shield-1",
        kind="defense",
        mana_cost=10,
        base_hit=100,
        base_damage=0,
        hit_modifier=0,
        damage_multiplier=1.0,
        shield=24,
        speed_bonus=0,
        dodge_bonus=0,
    )

    result = resolve_round(actor, defender, CombatAction(actor_id="char-lin-xuan", spell=spell), hit_roll=1)

    assert result.hit is True
    assert result.attacker_mana == 110
    assert result.attacker_shield == 24
    assert result.defender_life == 100
```

- [ ] **Step 2: Run combat tests to verify failure**

Run:

```bash
python -m pytest tests/test_combat.py -q
```

Expected: FAIL because `world_engine.combat` does not exist.

- [ ] **Step 3: Implement combat resolver**

Write `src/world_engine/combat.py`:

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Actor:
    id: str
    mana: int
    life: int
    attack: int
    defense: int
    speed: int
    hit_bonus: int
    dodge: int
    shield: int


@dataclass(frozen=True)
class Spell:
    id: str
    kind: str
    mana_cost: int
    base_hit: int
    base_damage: int
    hit_modifier: int
    damage_multiplier: float
    shield: int
    speed_bonus: int
    dodge_bonus: int


@dataclass(frozen=True)
class CombatAction:
    actor_id: str
    spell: Spell


@dataclass(frozen=True)
class RoundResult:
    hit: bool
    attacker_mana: int
    attacker_life: int
    attacker_shield: int
    defender_life: int
    defender_shield: int
    damage: int
    injury_state: str
    notes: list[str]


def injury_state(life: int) -> str:
    if life <= 0:
        return "defeated"
    if life <= 19:
        return "near_death"
    if life <= 39:
        return "severe_wound"
    if life <= 59:
        return "medium_wound"
    if life <= 79:
        return "light_wound"
    return "normal"


def resolve_round(attacker: Actor, defender: Actor, action: CombatAction, hit_roll: int) -> RoundResult:
    if action.actor_id != attacker.id:
        raise ValueError("action actor_id must match attacker id")
    if attacker.mana < action.spell.mana_cost:
        return RoundResult(
            hit=False,
            attacker_mana=attacker.mana,
            attacker_life=attacker.life,
            attacker_shield=attacker.shield,
            defender_life=defender.life,
            defender_shield=defender.shield,
            damage=0,
            injury_state=injury_state(defender.life),
            notes=["insufficient_mana"],
        )

    attacker_mana = attacker.mana - action.spell.mana_cost
    attacker_shield = attacker.shield
    defender_life = defender.life
    defender_shield = defender.shield
    notes: list[str] = []

    if action.spell.kind == "defense":
        attacker_shield += action.spell.shield
        notes.append("shield_added")
        return RoundResult(
            hit=True,
            attacker_mana=attacker_mana,
            attacker_life=attacker.life,
            attacker_shield=attacker_shield,
            defender_life=defender_life,
            defender_shield=defender_shield,
            damage=0,
            injury_state=injury_state(defender_life),
            notes=notes,
        )

    hit_target = action.spell.base_hit + attacker.hit_bonus + action.spell.hit_modifier - defender.dodge
    hit = hit_roll <= hit_target
    damage = 0
    if hit:
        raw_damage = round(action.spell.base_damage * action.spell.damage_multiplier + attacker.attack * 0.2)
        mitigated = max(0, raw_damage - round(defender.defense * 0.5))
        shield_absorb = min(defender_shield, mitigated)
        defender_shield -= shield_absorb
        damage = mitigated - shield_absorb
        defender_life = max(0, defender_life - damage)
        notes.append("hit")
    else:
        notes.append("miss")

    return RoundResult(
        hit=hit,
        attacker_mana=attacker_mana,
        attacker_life=attacker.life,
        attacker_shield=attacker_shield,
        defender_life=defender_life,
        defender_shield=defender_shield,
        damage=damage,
        injury_state=injury_state(defender_life),
        notes=notes,
    )
```

- [ ] **Step 4: Run combat tests**

Run:

```bash
python -m pytest tests/test_combat.py -q
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

If git is available:

```bash
git add src/world_engine/combat.py tests/test_combat.py
git commit -m "feat: resolve objective combat rounds"
```

---

### Task 9: CLI Commands

**Files:**
- Create: `src/world_engine/cli.py`
- Modify: `tests/test_validation.py`

- [ ] **Step 1: Add CLI smoke test**

Append to `tests/test_validation.py`:

```python
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
```

- [ ] **Step 2: Run CLI test to verify failure**

Run:

```bash
python -m pytest tests/test_validation.py::test_cli_validate_world_reports_ok -q
```

Expected: FAIL because `world_engine.cli` does not exist.

- [ ] **Step 3: Implement CLI**

Write `src/world_engine/cli.py`:

```python
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from world_engine.validation import validate_world


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="world-engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a world directory")
    validate.add_argument("world_root", type=Path)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        result = validate_world(args.world_root)
        if result.ok:
            print(f"valid: {args.world_root}")
            for warning in result.warnings:
                print(f"warning: {warning}")
            return 0
        for error in result.errors:
            print(f"error: {error}")
        return 1

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run CLI tests**

Run:

```bash
python -m pytest tests/test_validation.py::test_cli_validate_world_reports_ok -q
```

Expected: 1 passed.

- [ ] **Step 5: Run CLI against seeded world**

Run:

```bash
python -m world_engine.cli validate world
```

Expected: prints `valid: world` and exits with code 0.

- [ ] **Step 6: Commit**

If git is available:

```bash
git add src/world_engine/cli.py tests/test_validation.py
git commit -m "feat: add world validation cli"
```

---

### Task 10: Full Verification

**Files:**
- Modify only files required by failed tests discovered in this task.

- [ ] **Step 1: Run full test suite**

Run:

```bash
python -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Run seeded world validation**

Run:

```bash
python -m world_engine.cli validate world
```

Expected: prints `valid: world`.

- [ ] **Step 3: Run package import smoke check**

Run:

```bash
python - <<'PY'
from world_engine.cultivation import CultivationAction, calculate_cp_gain
from world_engine.breakthrough import BreakthroughCheck, calculate_success_rate
from world_engine.skills import stage_for_sp

print(calculate_cp_gain(CultivationAction(10, 1.0, 1.0, 1.0)).cp_gain)
print(calculate_success_rate(BreakthroughCheck(20, [35, 10], [], 95, 5)))
print(stage_for_sp(1200))
PY
```

Expected output:

```text
10
65
proficient
```

- [ ] **Step 4: Commit final verification updates**

If git is available and files changed during verification:

```bash
git add src tests world
git commit -m "test: verify cultivation world engine mvp"
```

If no files changed, do not create an empty commit.

---

## Self-Review Notes

Spec coverage:

- Persistent file world: covered by Tasks 3 and 4.
- Absolute truth versus knowledge: represented in starter character schema in Task 3.
- Materialized/indexed world: represented in entity index and Tiannan seed files in Task 3.
- Cultivation CP: covered by Task 5.
- Breakthrough probability: covered by Task 6.
- Skill SP and non-linear stages: covered by Task 7.
- Content rule library: covered by Task 3.
- Objective combat resolver: covered by Task 8.
- Scripts/CLI support: covered by Task 9.
- Verification: covered by Task 10.

Known deliberate limits:

- The combat resolver handles one action against one defender per round. Multi-combatant battle can be built after this is stable.
- The validator checks core references and materialized paths. Deeper schema validation can be added once the starter YAML structure survives first use.
- The first content library is small by design and supports outer-sect gameplay only.
