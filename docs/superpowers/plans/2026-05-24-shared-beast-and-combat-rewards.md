# Shared Beast And Combat Rewards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add reusable beast templates, material content, deterministic beast instance generation, and objective combat reward calculation to the shared ruleset.

**Architecture:** Keep universal definitions in `rulesets/classic_xianxia/content/` and world-specific instances in `worlds/...`. Add a focused `world_engine.beasts` module for template loading and instance generation, and a focused `world_engine.rewards` module for combat experience, skill SP, and material harvest outcomes. Extend validation so world beast instances and ruleset beast templates cannot reference unknown variants, materials, or invalid roll ranges.

**Tech Stack:** Python 3.12, dataclasses, pathlib, PyYAML through existing `world_engine.io`, pytest, YAML ruleset/world files.

---

## Scope Boundary

This plan implements the approved spec at `docs/superpowers/specs/2026-05-24-shared-beast-and-combat-rewards-design.md`.

Included:

- Shared beast template file for `beast-firestripe-wolf`.
- Shared material files for firestripe pelt, warm beast blood, and beast core fragment.
- Shared combat reward category rules.
- Beast template loading and deterministic instance generation from explicit multipliers.
- Material harvest calculation using roll values and condition requirements.
- Combat reward category calculation and skill SP multiplier output.
- Validation for beast template material references, world beast instances, variants, layers, and generation roll ranges.

Excluded:

- Full ecology simulation.
- Automatic world population generation.
- Advanced tactical AI.
- Global economy.
- UI for inspecting beast templates.

## File Map

- Create: `rulesets/classic_xianxia/content/beasts/firestripe_wolf.yaml` - shared firestripe wolf species template.
- Create: `rulesets/classic_xianxia/content/materials/firestripe_pelt.yaml` - shared material definition.
- Create: `rulesets/classic_xianxia/content/materials/warm_beast_blood.yaml` - shared material definition.
- Create: `rulesets/classic_xianxia/content/materials/beast_core_fragment.yaml` - shared material definition.
- Create: `rulesets/classic_xianxia/combat_rewards.yaml` - shared reward category rules.
- Create: `src/world_engine/beasts.py` - beast template loading and deterministic instance generation.
- Create: `src/world_engine/rewards.py` - combat reward and material harvest calculations.
- Modify: `src/world_engine/validation.py` - validate beast templates and world instances.
- Create: `tests/test_beasts.py` - beast generation tests.
- Create: `tests/test_rewards.py` - reward calculation tests.
- Modify: `tests/test_validation.py` - validation tests for beast/material references and instance rolls.

## Task 1: Add Shared Beast And Material Content

**Files:**
- Create: `rulesets/classic_xianxia/content/beasts/firestripe_wolf.yaml`
- Create: `rulesets/classic_xianxia/content/materials/firestripe_pelt.yaml`
- Create: `rulesets/classic_xianxia/content/materials/warm_beast_blood.yaml`
- Create: `rulesets/classic_xianxia/content/materials/beast_core_fragment.yaml`
- Create: `rulesets/classic_xianxia/combat_rewards.yaml`
- Test: `tests/test_beasts.py`

- [ ] **Step 1: Write failing content loading test**

Create `tests/test_beasts.py`:

```python
from pathlib import Path

from world_engine.beasts import load_beast_template


def test_load_firestripe_wolf_template_from_ruleset():
    template = load_beast_template(Path("rulesets/classic_xianxia"), "beast-firestripe-wolf")

    assert template["id"] == "beast-firestripe-wolf"
    assert template["type"] == "beast"
    assert template["variants"]["adult"]["layer_range"] == [2, 4]
    assert template["materials"][0]["id"] == "mat-firestripe-pelt"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
.venv/bin/python -m pytest tests/test_beasts.py::test_load_firestripe_wolf_template_from_ruleset -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'world_engine.beasts'`.

- [ ] **Step 3: Add shared beast template**

Create `rulesets/classic_xianxia/content/beasts/firestripe_wolf.yaml`:

```yaml
id: beast-firestripe-wolf
name: Firestripe Wolf
type: beast
species: firestripe_wolf
realm_band: qi_refining_beast
element_affinity:
  - fire
variants:
  juvenile:
    layer_range: [1, 2]
    stat_multipliers:
      life: 0.75
      attack: 0.75
      defense: 0.8
      speed: 1.05
  adult:
    layer_range: [2, 4]
    stat_multipliers:
      life: 1.0
      attack: 1.0
      defense: 1.0
      speed: 1.0
  elite:
    layer_range: [4, 6]
    stat_multipliers:
      life: 1.3
      attack: 1.25
      defense: 1.15
      speed: 1.1
base_combat:
  layer_1:
    mana_max: 25
    life: 70
    attack: 14
    defense: 6
    speed: 14
    divine_sense: 3
    control_resistance: 3
    poison_resistance: 2
  layer_scaling:
    mana_max: 12
    life: 18
    attack: 5
    defense: 3
    speed: 2
    divine_sense: 1
abilities:
  bite:
    type: physical_attack
    base_hit: 70
    base_damage: 18
  ember_pounce:
    type: fire_attack
    mana_cost: 8
    base_hit: 62
    base_damage: 24
materials:
  - id: mat-firestripe-pelt
    chance: 0.75
    condition_requirements:
      corpse_not_burned: true
  - id: mat-warm-beast-blood
    chance: 0.6
    condition_requirements:
      harvested_within_hours: 2
  - id: mat-beast-core-fragment
    chance: 0.15
    condition_requirements:
      layer_min: 3
growth:
  age_stages:
    juvenile_days: [0, 180]
    adult_days: [181, 1200]
    old_days: [1201, 1800]
  growth_inputs:
    - time
    - feeding
    - spiritual_environment
    - combat_survival
behavior:
  aggression: territorial
  preferred_environment:
    - fire_warm_woods
    - dry_ridge
```

- [ ] **Step 4: Add shared material definitions**

Create `rulesets/classic_xianxia/content/materials/firestripe_pelt.yaml`:

```yaml
id: mat-firestripe-pelt
name: Firestripe Pelt
type: material
grade: first_rank_lower
uses:
  - low_grade_artifact_material
  - sect_task_turn_in
  - trade
quality_factors:
  damaged_by_fire: lowers_value
  clean_harvest: preserves_value
```

Create `rulesets/classic_xianxia/content/materials/warm_beast_blood.yaml`:

```yaml
id: mat-warm-beast-blood
name: Warm Beast Blood
type: material
grade: first_rank_lower
uses:
  - fire_aspect_pill_material
  - talisman_ink
  - trade
quality_factors:
  harvested_quickly: preserves_value
  delayed_harvest: spoils_value
```

Create `rulesets/classic_xianxia/content/materials/beast_core_fragment.yaml`:

```yaml
id: mat-beast-core-fragment
name: Beast Core Fragment
type: material
grade: first_rank_lower
uses:
  - cultivation_support
  - artifact_material
  - sect_task_turn_in
  - trade
quality_factors:
  intact_extraction: preserves_value
  failed_extraction: destroys_material
```

- [ ] **Step 5: Add shared combat reward rules**

Create `rulesets/classic_xianxia/combat_rewards.yaml`:

```yaml
id: rules-combat-rewards-v1
reward_categories:
  trivial:
    combat_experience: 0
    skill_sp_multiplier: 0.1
  low:
    combat_experience: 1
    skill_sp_multiplier: 0.5
  standard:
    combat_experience: 2
    skill_sp_multiplier: 1.0
  dangerous:
    combat_experience: 4
    skill_sp_multiplier: 1.5
  life_threatening:
    combat_experience: 8
    skill_sp_multiplier: 2.0
relative_strength_thresholds:
  trivial_max: 0.4
  low_max: 0.75
  standard_max: 1.25
  dangerous_max: 1.75
anti_farming:
  repeated_low_risk_same_target_limit: 2
  trivial_repeat_combat_experience: 0
```

- [ ] **Step 6: Implement minimal template loader**

Create `src/world_engine/beasts.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

from world_engine.io import WorldDataError, load_yaml


def load_beast_template(ruleset_path: Path, beast_id: str) -> dict[str, Any]:
    content_root = ruleset_path / "content" / "beasts"
    if not content_root.exists():
        raise WorldDataError(f"beast content directory does not exist: {content_root}")

    for path in content_root.rglob("*.yaml"):
        data = load_yaml(path)
        if data.get("id") == beast_id:
            return data

    raise WorldDataError(f"beast template does not exist: {beast_id}")
```

- [ ] **Step 7: Run template loading test**

Run:

```bash
.venv/bin/python -m pytest tests/test_beasts.py::test_load_firestripe_wolf_template_from_ruleset -q
```

Expected: PASS.

- [ ] **Step 8: Commit**

Run:

```bash
git add rulesets/classic_xianxia/content/beasts/firestripe_wolf.yaml rulesets/classic_xianxia/content/materials/firestripe_pelt.yaml rulesets/classic_xianxia/content/materials/warm_beast_blood.yaml rulesets/classic_xianxia/content/materials/beast_core_fragment.yaml rulesets/classic_xianxia/combat_rewards.yaml src/world_engine/beasts.py tests/test_beasts.py
git commit -m "feat: add shared beast content"
```

Expected: commit succeeds.

## Task 2: Generate Deterministic Beast Instances

**Files:**
- Modify: `src/world_engine/beasts.py`
- Modify: `tests/test_beasts.py`

- [ ] **Step 1: Add failing instance generation tests**

Append to `tests/test_beasts.py`:

```python
from world_engine.beasts import generate_beast_instance


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
    assert instance["combat"]["speed"] == 20


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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_beasts.py::test_generate_adult_firestripe_wolf_instance_with_recorded_rolls tests/test_beasts.py::test_generate_beast_instance_rejects_layer_outside_variant_range -q
```

Expected: FAIL with `ImportError` for `generate_beast_instance`.

- [ ] **Step 3: Implement instance generation**

Append to `src/world_engine/beasts.py`:

```python
ROLL_KEYS = (
    "life_multiplier",
    "mana_multiplier",
    "attack_multiplier",
    "defense_multiplier",
    "speed_multiplier",
)


def generate_beast_instance(
    *,
    template: dict[str, Any],
    instance_id: str,
    variant: str,
    layer: int,
    location: str,
    seed: str,
    rolls: dict[str, float],
    growth_state: dict[str, str],
) -> dict[str, Any]:
    variants = template.get("variants", {})
    if not isinstance(variants, dict) or variant not in variants:
        raise ValueError(f"unknown beast variant: {variant}")

    variant_data = variants[variant]
    if not isinstance(variant_data, dict):
        raise ValueError(f"beast variant must be a mapping: {variant}")

    layer_min, layer_max = _layer_range(variant, variant_data)
    if layer < layer_min or layer > layer_max:
        raise ValueError(f"layer {layer} is outside variant {variant} range: {layer_min}-{layer_max}")

    _validate_rolls(rolls)
    combat = _scaled_combat(template, variant_data, layer, rolls)
    return {
        "id": instance_id,
        "template": template["id"],
        "variant": variant,
        "realm": template["realm_band"],
        "layer": layer,
        "state": "alive",
        "location": location,
        "generation": {
            "method": "template_variant_roll",
            "seed": seed,
            "rolls": dict(rolls),
        },
        "combat": combat,
        "conditions": [],
        "growth_state": dict(growth_state),
        "growth_history": [],
        "material_state": {
            "corpse_condition": None,
            "harvested": [],
        },
        "event_history": [],
    }


def _layer_range(variant: str, variant_data: dict[str, Any]) -> tuple[int, int]:
    value = variant_data.get("layer_range")
    if (
        not isinstance(value, list)
        or len(value) != 2
        or not isinstance(value[0], int)
        or not isinstance(value[1], int)
    ):
        raise ValueError(f"variant {variant} must define layer_range as two integers")
    return value[0], value[1]


def _validate_rolls(rolls: dict[str, float]) -> None:
    for key in ROLL_KEYS:
        value = rolls.get(key)
        if not isinstance(value, int | float):
            raise ValueError(f"missing beast generation roll: {key}")
        if value < 0.9 or value > 1.1:
            raise ValueError(f"beast generation roll {key} out of range: {value}")


def _scaled_combat(
    template: dict[str, Any],
    variant_data: dict[str, Any],
    layer: int,
    rolls: dict[str, float],
) -> dict[str, int]:
    base_combat = template["base_combat"]
    layer_1 = base_combat["layer_1"]
    scaling = base_combat["layer_scaling"]
    variant_multipliers = variant_data.get("stat_multipliers", {})

    def scaled(stat: str, roll_key: str | None = None) -> int:
        base = int(layer_1[stat]) + int(scaling.get(stat, 0)) * (layer - 1)
        variant_multiplier = float(variant_multipliers.get(stat, 1.0))
        roll_multiplier = float(rolls.get(roll_key or f"{stat}_multiplier", 1.0))
        return round(base * variant_multiplier * roll_multiplier)

    mana_max = scaled("mana_max", "mana_multiplier")
    return {
        "mana_max": mana_max,
        "mana_current": mana_max,
        "life": scaled("life", "life_multiplier"),
        "attack": scaled("attack", "attack_multiplier"),
        "defense": scaled("defense", "defense_multiplier"),
        "speed": scaled("speed", "speed_multiplier"),
        "divine_sense": scaled("divine_sense", None),
        "control_resistance": scaled("control_resistance", None),
        "poison_resistance": scaled("poison_resistance", None),
    }
```

- [ ] **Step 4: Run instance generation tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_beasts.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add src/world_engine/beasts.py tests/test_beasts.py
git commit -m "feat: generate beast instances"
```

Expected: commit succeeds.

## Task 3: Calculate Combat Rewards

**Files:**
- Create: `src/world_engine/rewards.py`
- Create: `tests/test_rewards.py`

- [ ] **Step 1: Write failing reward tests**

Create `tests/test_rewards.py`:

```python
from pathlib import Path

from world_engine.io import load_yaml
from world_engine.rewards import CombatRewardInput, calculate_combat_reward


def test_calculate_standard_combat_reward():
    rules = load_yaml(Path("rulesets/classic_xianxia/combat_rewards.yaml"))
    result = calculate_combat_reward(
        rules,
        CombatRewardInput(
            enemy_relative_strength=1.0,
            actual_risk="standard",
            rounds_survived=3,
            meaningful_actions=2,
            outcome="victory",
            repeated_low_risk_count=0,
            used_skill_ids=["spell-fireball-1"],
        ),
    )

    assert result.category == "standard"
    assert result.combat_experience == 2
    assert result.skill_sp_multiplier == 1.0
    assert result.skill_ids == ["spell-fireball-1"]


def test_repeated_trivial_fight_awards_no_combat_experience():
    rules = load_yaml(Path("rulesets/classic_xianxia/combat_rewards.yaml"))
    result = calculate_combat_reward(
        rules,
        CombatRewardInput(
            enemy_relative_strength=0.2,
            actual_risk="low",
            rounds_survived=1,
            meaningful_actions=1,
            outcome="victory",
            repeated_low_risk_count=5,
            used_skill_ids=["spell-fireball-1"],
        ),
    )

    assert result.category == "trivial"
    assert result.combat_experience == 0
    assert result.skill_sp_multiplier == 0.1
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_rewards.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'world_engine.rewards'`.

- [ ] **Step 3: Implement combat reward calculation**

Create `src/world_engine/rewards.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CombatRewardInput:
    enemy_relative_strength: float
    actual_risk: str
    rounds_survived: int
    meaningful_actions: int
    outcome: str
    repeated_low_risk_count: int
    used_skill_ids: list[str]


@dataclass(frozen=True)
class CombatRewardResult:
    category: str
    combat_experience: int
    skill_sp_multiplier: float
    skill_ids: list[str]


RISK_ORDER = {
    "trivial": 0,
    "low": 1,
    "standard": 2,
    "dangerous": 3,
    "life_threatening": 4,
}


def calculate_combat_reward(
    rules: dict[str, Any],
    reward_input: CombatRewardInput,
) -> CombatRewardResult:
    category = _category_from_relative_strength(rules, reward_input.enemy_relative_strength)
    if RISK_ORDER.get(reward_input.actual_risk, 0) > RISK_ORDER[category]:
        category = reward_input.actual_risk

    anti_farming = rules.get("anti_farming", {})
    repeat_limit = int(anti_farming.get("repeated_low_risk_same_target_limit", 2))
    if (
        reward_input.enemy_relative_strength <= float(rules["relative_strength_thresholds"]["trivial_max"])
        and reward_input.repeated_low_risk_count > repeat_limit
    ):
        category = "trivial"

    reward_categories = rules["reward_categories"]
    reward_data = reward_categories[category]
    return CombatRewardResult(
        category=category,
        combat_experience=int(reward_data["combat_experience"]),
        skill_sp_multiplier=float(reward_data["skill_sp_multiplier"]),
        skill_ids=list(reward_input.used_skill_ids),
    )


def _category_from_relative_strength(rules: dict[str, Any], relative_strength: float) -> str:
    thresholds = rules["relative_strength_thresholds"]
    if relative_strength <= float(thresholds["trivial_max"]):
        return "trivial"
    if relative_strength <= float(thresholds["low_max"]):
        return "low"
    if relative_strength <= float(thresholds["standard_max"]):
        return "standard"
    if relative_strength <= float(thresholds["dangerous_max"]):
        return "dangerous"
    return "life_threatening"
```

- [ ] **Step 4: Run reward tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_rewards.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add src/world_engine/rewards.py tests/test_rewards.py
git commit -m "feat: calculate combat rewards"
```

Expected: commit succeeds.

## Task 4: Calculate Material Harvest Outcomes

**Files:**
- Modify: `src/world_engine/rewards.py`
- Modify: `tests/test_rewards.py`

- [ ] **Step 1: Add failing material harvest tests**

Append to `tests/test_rewards.py`:

```python
from world_engine.beasts import load_beast_template
from world_engine.rewards import HarvestContext, calculate_material_harvest


def test_calculate_material_harvest_respects_rolls_and_conditions():
    template = load_beast_template(Path("rulesets/classic_xianxia"), "beast-firestripe-wolf")

    result = calculate_material_harvest(
        template,
        beast_layer=3,
        context=HarvestContext(
            corpse_not_burned=True,
            harvested_within_hours=1,
            extraction_skill="basic",
        ),
        rolls={
            "mat-firestripe-pelt": 0.4,
            "mat-warm-beast-blood": 0.5,
            "mat-beast-core-fragment": 0.1,
        },
    )

    assert result.obtained_material_ids == [
        "mat-firestripe-pelt",
        "mat-warm-beast-blood",
        "mat-beast-core-fragment",
    ]
    assert result.failed_material_ids == []


def test_calculate_material_harvest_blocks_burned_pelt_and_late_blood():
    template = load_beast_template(Path("rulesets/classic_xianxia"), "beast-firestripe-wolf")

    result = calculate_material_harvest(
        template,
        beast_layer=3,
        context=HarvestContext(
            corpse_not_burned=False,
            harvested_within_hours=4,
            extraction_skill="basic",
        ),
        rolls={
            "mat-firestripe-pelt": 0.1,
            "mat-warm-beast-blood": 0.1,
            "mat-beast-core-fragment": 0.9,
        },
    )

    assert result.obtained_material_ids == []
    assert result.failed_material_ids == [
        "mat-firestripe-pelt",
        "mat-warm-beast-blood",
        "mat-beast-core-fragment",
    ]
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_rewards.py::test_calculate_material_harvest_respects_rolls_and_conditions tests/test_rewards.py::test_calculate_material_harvest_blocks_burned_pelt_and_late_blood -q
```

Expected: FAIL with `ImportError` for `HarvestContext` or `calculate_material_harvest`.

- [ ] **Step 3: Implement material harvest calculation**

Append to `src/world_engine/rewards.py`:

```python
@dataclass(frozen=True)
class HarvestContext:
    corpse_not_burned: bool
    harvested_within_hours: int
    extraction_skill: str


@dataclass(frozen=True)
class MaterialHarvestResult:
    obtained_material_ids: list[str]
    failed_material_ids: list[str]


def calculate_material_harvest(
    beast_template: dict[str, Any],
    *,
    beast_layer: int,
    context: HarvestContext,
    rolls: dict[str, float],
) -> MaterialHarvestResult:
    obtained: list[str] = []
    failed: list[str] = []
    materials = beast_template.get("materials", [])
    if not isinstance(materials, list):
        return MaterialHarvestResult(obtained_material_ids=[], failed_material_ids=[])

    for material in materials:
        if not isinstance(material, dict):
            continue
        material_id = material["id"]
        chance = float(material["chance"])
        roll = rolls.get(material_id)
        if roll is None:
            raise ValueError(f"missing harvest roll for material: {material_id}")

        if _requirements_met(material.get("condition_requirements", {}), beast_layer, context) and roll <= chance:
            obtained.append(material_id)
        else:
            failed.append(material_id)

    return MaterialHarvestResult(obtained_material_ids=obtained, failed_material_ids=failed)


def _requirements_met(
    requirements: object,
    beast_layer: int,
    context: HarvestContext,
) -> bool:
    if not isinstance(requirements, dict):
        return True

    if requirements.get("corpse_not_burned") is True and not context.corpse_not_burned:
        return False

    harvested_limit = requirements.get("harvested_within_hours")
    if isinstance(harvested_limit, int) and context.harvested_within_hours > harvested_limit:
        return False

    layer_min = requirements.get("layer_min")
    if isinstance(layer_min, int) and beast_layer < layer_min:
        return False

    return True
```

- [ ] **Step 4: Run all reward tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_rewards.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

Run:

```bash
git add src/world_engine/rewards.py tests/test_rewards.py
git commit -m "feat: calculate material harvests"
```

Expected: commit succeeds.

## Task 5: Validate Beast Templates And World Instances

**Files:**
- Modify: `src/world_engine/validation.py`
- Modify: `tests/test_validation.py`

- [ ] **Step 1: Add failing validation tests**

Append to `tests/test_validation.py`:

```python
def test_validate_world_reports_beast_instance_unknown_template(tmp_path: Path):
    write(tmp_path / "rulesets/classic_xianxia/cultivation.yaml", "id: rules-cultivation-v1\n")
    write(tmp_path / "rulesets/classic_xianxia/actions.yaml", "id: rules-actions-v1\n")
    write(
        tmp_path / "worlds/xuanyuan/world.yaml",
        "id: world-test\nactive_subject: char-a\nruleset: classic_xianxia\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: chars/a.yaml\n  beast-a:\n    type: beast\n    state: materialized\n    path: beasts/a.yaml\n",
    )
    write(tmp_path / "worlds/xuanyuan/chars/a.yaml", "id: char-a\nname: A\n")
    write(
        tmp_path / "worlds/xuanyuan/beasts/a.yaml",
        "id: beast-a\ntemplate: beast-missing\nvariant: adult\nlayer: 3\ngeneration:\n  rolls:\n    life_multiplier: 1.0\n",
    )

    result = validate_world(tmp_path / "worlds/xuanyuan")

    assert "beast beast-a references missing beast template: beast-missing" in result.errors


def test_validate_world_reports_beast_instance_bad_variant_layer_and_roll(tmp_path: Path):
    write(tmp_path / "rulesets/classic_xianxia/cultivation.yaml", "id: rules-cultivation-v1\n")
    write(tmp_path / "rulesets/classic_xianxia/actions.yaml", "id: rules-actions-v1\n")
    write(
        tmp_path / "rulesets/classic_xianxia/content/beasts/firestripe_wolf.yaml",
        "id: beast-firestripe-wolf\ntype: beast\nvariants:\n  juvenile:\n    layer_range: [1, 2]\nmaterials: []\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/world.yaml",
        "id: world-test\nactive_subject: char-a\nruleset: classic_xianxia\n",
    )
    write(
        tmp_path / "worlds/xuanyuan/indexes/entities.yaml",
        "id: index-entities\nentities:\n  char-a:\n    type: character\n    state: materialized\n    path: chars/a.yaml\n  beast-a:\n    type: beast\n    state: materialized\n    path: beasts/a.yaml\n",
    )
    write(tmp_path / "worlds/xuanyuan/chars/a.yaml", "id: char-a\nname: A\n")
    write(
        tmp_path / "worlds/xuanyuan/beasts/a.yaml",
        "id: beast-a\ntemplate: beast-firestripe-wolf\nvariant: juvenile\nlayer: 4\ngeneration:\n  rolls:\n    life_multiplier: 1.2\n",
    )

    result = validate_world(tmp_path / "worlds/xuanyuan")

    assert "beast beast-a layer 4 is outside variant juvenile range: 1-2" in result.errors
    assert "beast beast-a generation roll life_multiplier out of range: 1.2" in result.errors
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_validation.py::test_validate_world_reports_beast_instance_unknown_template tests/test_validation.py::test_validate_world_reports_beast_instance_bad_variant_layer_and_roll -q
```

Expected: FAIL because validation does not inspect beast instances.

- [ ] **Step 3: Extend validation beast collection**

Modify `src/world_engine/validation.py`.

Add variables after `content_by_id`:

```python
    beast_templates: dict[str, dict[str, object]] = {}
```

Inside the ruleset exists block, after `content_by_id = _collect_content_by_id(ruleset_path)`, add:

```python
            beast_templates = _collect_beast_templates(ruleset_path)
```

Update `_validate_entity_ruleset_references(...)` call to pass `beast_templates` before `errors`.

Add helper:

```python
def _collect_beast_templates(ruleset_path: Path) -> dict[str, dict[str, object]]:
    beast_root = ruleset_path / "content" / "beasts"
    if not beast_root.exists():
        return {}

    templates: dict[str, dict[str, object]] = {}
    for path in beast_root.rglob("*.yaml"):
        try:
            data = load_yaml(path)
        except WorldDataError:
            continue
        beast_id = data.get("id")
        if isinstance(beast_id, str):
            templates[beast_id] = data
    return templates
```

Update `_validate_entity_ruleset_references` signature to include:

```python
    beast_templates: dict[str, dict[str, object]],
```

- [ ] **Step 4: Add beast instance validation helper**

Add this call at the end of `_validate_entity_ruleset_references`:

```python
    if entity_type == "beast":
        _validate_beast_instance(entity_id, entity_data, beast_templates, errors)
```

Add helper:

```python
def _validate_beast_instance(
    entity_id: str,
    entity_data: dict[str, object],
    beast_templates: dict[str, dict[str, object]],
    errors: list[str],
) -> None:
    template_id = entity_data.get("template")
    if not isinstance(template_id, str):
        errors.append(f"beast {entity_id} has no template")
        return

    template = beast_templates.get(template_id)
    if template is None:
        errors.append(f"beast {entity_id} references missing beast template: {template_id}")
        return

    variant = entity_data.get("variant")
    variants = template.get("variants", {})
    if not isinstance(variant, str) or not isinstance(variants, dict) or variant not in variants:
        errors.append(f"beast {entity_id} references missing variant: {variant}")
        return

    variant_data = variants[variant]
    if isinstance(variant_data, dict):
        _validate_beast_layer(entity_id, entity_data, variant, variant_data, errors)

    generation = entity_data.get("generation", {})
    rolls = generation.get("rolls", {}) if isinstance(generation, dict) else {}
    if isinstance(rolls, dict):
        for key, value in rolls.items():
            if isinstance(value, int | float) and (value < 0.9 or value > 1.1):
                errors.append(f"beast {entity_id} generation roll {key} out of range: {value}")


def _validate_beast_layer(
    entity_id: str,
    entity_data: dict[str, object],
    variant: str,
    variant_data: dict[str, object],
    errors: list[str],
) -> None:
    layer = entity_data.get("layer")
    layer_range = variant_data.get("layer_range")
    if not isinstance(layer, int) or not isinstance(layer_range, list) or len(layer_range) != 2:
        return
    layer_min, layer_max = layer_range
    if not isinstance(layer_min, int) or not isinstance(layer_max, int):
        return
    if layer < layer_min or layer > layer_max:
        errors.append(f"beast {entity_id} layer {layer} is outside variant {variant} range: {layer_min}-{layer_max}")
```

- [ ] **Step 5: Run targeted validation tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_validation.py::test_validate_world_reports_beast_instance_unknown_template tests/test_validation.py::test_validate_world_reports_beast_instance_bad_variant_layer_and_roll -q
```

Expected: PASS.

- [ ] **Step 6: Validate current worlds**

Run:

```bash
.venv/bin/python -m world_engine.cli validate worlds/qinglan_frontier
.venv/bin/python -m world_engine.cli validate worlds/xuanyuan
```

Expected:

```text
valid: worlds/qinglan_frontier
valid: worlds/xuanyuan
```

- [ ] **Step 7: Commit**

Run:

```bash
git add src/world_engine/validation.py tests/test_validation.py
git commit -m "feat: validate beast instances"
```

Expected: commit succeeds.

## Task 6: Validate Beast Template Material References

**Files:**
- Modify: `src/world_engine/validation.py`
- Modify: `tests/test_validation.py`

- [ ] **Step 1: Add failing beast template validation test**

Append to `tests/test_validation.py`:

```python
def test_validate_world_reports_beast_template_unknown_material(tmp_path: Path):
    write(tmp_path / "rulesets/classic_xianxia/cultivation.yaml", "id: rules-cultivation-v1\n")
    write(tmp_path / "rulesets/classic_xianxia/actions.yaml", "id: rules-actions-v1\n")
    write(
        tmp_path / "rulesets/classic_xianxia/content/beasts/firestripe_wolf.yaml",
        "id: beast-firestripe-wolf\ntype: beast\nvariants: {}\nmaterials:\n  - id: mat-missing\n",
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

    assert "beast template beast-firestripe-wolf references missing material id: mat-missing" in result.errors
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
.venv/bin/python -m pytest tests/test_validation.py::test_validate_world_reports_beast_template_unknown_material -q
```

Expected: FAIL because template materials are not validated.

- [ ] **Step 3: Validate beast template materials**

In `validate_world`, after `beast_templates = _collect_beast_templates(ruleset_path)`, add:

```python
            _validate_beast_template_materials(beast_templates, content_by_id, errors)
```

Add helper:

```python
def _validate_beast_template_materials(
    beast_templates: dict[str, dict[str, object]],
    content_by_id: dict[str, dict[str, object]],
    errors: list[str],
) -> None:
    for beast_id, template in beast_templates.items():
        materials = template.get("materials", [])
        if not isinstance(materials, list):
            continue
        for material in materials:
            if not isinstance(material, dict):
                continue
            material_id = material.get("id")
            if isinstance(material_id, str) and material_id not in content_by_id:
                errors.append(
                    f"beast template {beast_id} references missing material id: {material_id}"
                )
```

- [ ] **Step 4: Run template material validation test**

Run:

```bash
.venv/bin/python -m pytest tests/test_validation.py::test_validate_world_reports_beast_template_unknown_material -q
```

Expected: PASS.

- [ ] **Step 5: Run all validation tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_validation.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add src/world_engine/validation.py tests/test_validation.py
git commit -m "feat: validate beast template materials"
```

Expected: commit succeeds.

## Task 7: Final Verification

**Files:**
- No file changes expected.

- [ ] **Step 1: Run full test suite**

Run:

```bash
.venv/bin/python -m pytest -q
```

Expected: all tests pass.

- [ ] **Step 2: Validate both world saves**

Run:

```bash
.venv/bin/python -m world_engine.cli validate worlds/qinglan_frontier
.venv/bin/python -m world_engine.cli validate worlds/xuanyuan
```

Expected:

```text
valid: worlds/qinglan_frontier
valid: worlds/xuanyuan
```

- [ ] **Step 3: Inspect git status**

Run:

```bash
git status --short
```

Expected: no uncommitted implementation changes from this plan. Pre-existing uncommitted world-play changes may still appear; do not revert them.

- [ ] **Step 4: Report completion**

Final response should include:

- tests run and result
- world validation result
- key APIs: `generate_beast_instance`, `calculate_combat_reward`, `calculate_material_harvest`
- note that shared definitions now live in the ruleset and world files should only store instances
