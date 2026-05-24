# Shared Beast And Combat Rewards Design

Date: 2026-05-24

## Purpose

Combat content must be objective and reusable across worlds. A beast, spell, equipment item, pill, material, or reward rule should not be invented differently for each world unless that world explicitly uses a different ruleset.

This design adds shared beast templates, material definitions, and combat reward rules to the reusable ruleset. World saves only store concrete instances, ownership, location, damage, growth history, and event outcomes.

## Core Principles

- Shared content lives in `rulesets/<ruleset>/content/`.
- World saves store instances and history, not universal definitions.
- Beast stats are determined by species, variant, realm/layer, state, and recorded instance rolls.
- Instance rolls are allowed, but they must be explicit and persisted.
- A material or reward is not granted automatically just because combat happened.
- Combat experience and loot depend on risk, enemy strength, battle outcome, corpse condition, harvesting ability, and task context.
- The LLM narrates results after mechanical resolution; it must not alter stat blocks, rewards, or drops arbitrarily.

## Ruleset Content Layout

Add shared content categories:

```text
rulesets/classic_xianxia/
  combat_rewards.yaml
  content/
    beasts/
      firestripe_wolf.yaml
    materials/
      firestripe_pelt.yaml
      warm_beast_blood.yaml
      beast_core_fragment.yaml
```

Existing spells, equipment, consumables, and status effects remain in the ruleset content library. Worlds can reference these content ids.

## Beast Template Model

A beast template defines a reusable species or beast type.

Required fields:

- `id`
- `name`
- `type: beast`
- `species`
- `realm_band`
- `element_affinity`
- `variants`
- `base_combat`
- `abilities`
- `materials`
- `growth`
- `behavior`

Example:

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

## Beast Instance Model

Worlds materialize concrete beasts only when touched by subject action, nearby causal chains, tasks, or return progression.

World instance files live under the relevant world location, for example:

```text
worlds/qinglan_frontier/continents/eastern_wilds/materialized/qinglan_frontier/wild_sites/demonwood_forest/beasts/firestripe_wolf_001.yaml
```

Instance fields:

```yaml
id: beast-firestripe-wolf-demonwood-001
template: beast-firestripe-wolf
variant: adult
realm: qi_refining_beast
layer: 3
state: alive
location: qinglan-demonwood-forest
generation:
  method: template_variant_roll
  seed: qinglan-73-02-13-demonwood-pack-a-001
  rolls:
    life_multiplier: 1.08
    attack_multiplier: 0.96
    defense_multiplier: 1.02
    speed_multiplier: 1.04
combat:
  mana_max: 49
  mana_current: 49
  life: 134
  attack: 23
  defense: 12
  speed: 20
  divine_sense: 5
  control_resistance: 5
  poison_resistance: 3
conditions: []
growth_state:
  age_stage: adult
  recent_feeding: good
  spiritual_environment: low_fire_aspect
growth_history: []
material_state:
  corpse_condition: null
  harvested:
    - none
event_history: []
```

Once written, these numbers are world truth. Future changes require events such as injury, healing, feeding, breakthrough, aging, mutation, or environmental shifts.

## Instance Roll Rules

Rolls provide variation without arbitrary narration.

Allowed first-version roll bands:

- life multiplier: `0.9` to `1.1`
- mana multiplier: `0.9` to `1.1`
- attack multiplier: `0.9` to `1.1`
- defense multiplier: `0.9` to `1.1`
- speed multiplier: `0.9` to `1.1`

Elite, injured, starving, old, or mutated variants apply template-defined modifiers before or after instance rolls as specified by the template.

Every roll must be stored under `generation.rolls`. If randomness is used, store the seed or roll values. If deterministic generation is used, store the method and computed multipliers.

## Growth Rules

Beasts may become stronger over time, but only through defined causes:

- age progression
- feeding
- spiritual environment
- surviving combat
- mutation event
- breakthrough event
- injury recovery

Growth changes must be recorded in `growth_history` with time, cause, and stat changes.

Example:

```yaml
growth_history:
  - time:
      calendar: Qingyang
      year: 73
      month: 4
      day: 2
    cause: repeated_feeding_on_fire_aspect_herbs
    changes:
      layer: 3_to_4
      attack: 23_to_28
      mana_max: 49_to_61
```

## Combat Experience Rewards

Combat experience is a character stat representing practical battle judgment. It should affect later combat through modest bonuses such as hit bonus, dodge, initiative, escape judgment, and resistance to panic.

Reward inputs:

- enemy relative strength
- actual risk
- rounds survived
- meaningful actions taken
- victory, escape, defeat, or rescue
- whether the fight was repeated low-risk farming
- wounds and resource cost
- whether the subject used relevant skills under pressure

First-version reward categories:

```yaml
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
```

No combat experience should be awarded for staged, riskless repetition beyond minimal training benefit. Practice dummies and supervised drills belong to training SP, not real combat experience, unless something goes wrong.

## Skill SP From Combat

Using a skill in real combat can grant SP when it matters.

Examples:

- Fireball is cast under pressure and affects the outcome: grants Fireball SP.
- A defensive spell prevents injury: grants that defensive spell SP.
- A miss can still grant small SP if the action was real and the user learns from it.
- Repeatedly using a mastered skill against helpless targets grants little or no SP.

SP gain should be calculated separately from combat experience and respect existing skill thresholds.

## Material Rewards

Materials come from the defeated beast's template and the concrete condition of the instance.

Material reward inputs:

- beast template material table
- corpse condition
- damage type
- harvest timing
- character harvesting knowledge
- tools
- whether the beast fled, was destroyed, or was captured
- task requirements

Examples:

- Burning a firestripe wolf may reduce pelt quality.
- Killing with clean cuts may preserve hide and fangs.
- Delayed harvesting may spoil blood.
- A low-level cultivator may fail to extract a core fragment even if one exists.

Materials are concrete inventory items once obtained. They can be used for:

- alchemy
- artifact crafting
- talisman ink
- sect task turn-in
- trade
- special cultivation or spell practice if a rule explicitly allows it

## Task And Economy Integration

The same material can have several values depending on context.

Example:

- `mat-firestripe-pelt` can be sold at a market.
- It can satisfy a sect mission.
- It can be used by an artifact crafter.
- It can be damaged and become low-quality material.

Worlds store market prices, sect demand, and local scarcity. The ruleset stores the material's base identity and allowed uses.

## Validation

World validation should check:

- beast instance `template` references an existing ruleset beast id
- material ids referenced by beast templates exist
- ability ids or inline abilities have required combat fields
- instance `variant` exists in template
- instance `layer` is within variant layer range unless an override event exists
- generation roll multipliers are within allowed ranges
- world inventories reference known material ids

Ruleset validation should check:

- beast templates have required fields
- material content files have ids and declared uses
- combat reward categories are well formed

## Non-Goals

This design does not implement full ecology, automatic beast population simulation, advanced AI tactics, or a global economy. It establishes deterministic shared content, explicit instance variation, growth history, and objective combat rewards.
