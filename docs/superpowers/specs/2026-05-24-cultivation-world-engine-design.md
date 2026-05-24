# Cultivation World Engine Design

Date: 2026-05-24

## Purpose

This project builds a persistent cultivation world that can expand indefinitely, preserve history, and evolve around an active subject without turning the subject's claims into truth. The world should feel alive, but its rules must remain stable.

The active subject is a point of narrative focus, not an exception to the rules. Events near the subject are sampled at higher resolution, while distant places remain coarse, indexed, frozen, or summarized until touched.

## Core Principles

- Rules constrain the world.
- The LLM evolves the world.
- Scripts maintain, calculate, check, and summarize the world.
- Claims are not facts.
- Actions and verified outcomes change the true world state.
- The world has absolute truth, but characters only hold partial or mistaken knowledge.
- World causality is equal, but narrative resolution is unequal.

## Truth And Knowledge

The world has two separate layers.

The absolute truth layer records real cultivation level, talent, lifespan, wounds, hidden identity, resources, secrets, and causal history. This layer is not automatically known by any character.

The knowledge layer records what each character, sect, city, or organization believes. A subject saying "I am a peerless genius" creates a claim or rumor, not a talent change. Other characters may believe, doubt, mock, exploit, or ignore that claim based on their own knowledge and interests.

## Time Progression

Time advances according to the subject's consumed time.

- Immediate progression: conversations, trades, single choices, combat exchanges, inspections.
- Day-end progression: fatigue, close relationships, room-mates, local rumors, direct enemies.
- Ten-day progression: cultivation sessions, alchemy, healing, travel, task completion.
- Monthly progression: sect allowance, facility inventory, city conditions, local faction shifts.
- Yearly progression: regional summaries, aging, long seclusion, major faction movement.
- Return progression: when a frozen area is revisited after a long time.

Nearby characters do not freeze while the subject acts. If the subject spends three days in a sect, room-mates, teachers, enemies, facilities, and close hooks also move through those three days. Far areas are not fully simulated during that period.

## Region Materialization

The world can be much larger than the materialized file tree.

Entities have three existence states:

- Conceptual: possible in the world, unnamed or undefined.
- Indexed: named and roughly described, but not expanded into files.
- Materialized: touched by the subject, a main storyline, or an important causal chain, and represented by files.

Large regions such as continents should not pre-generate all nations, sects, cities, facilities, or characters. They keep high-level indexes and rumors. When the subject touches a sect, city, residence, shop, or facility, that part becomes materialized.

When the subject leaves a major area and no important viewpoint remains there, the area can freeze. If the subject returns hundreds of years later, the system performs return progression: lifespan resolution, old character death or breakthrough, faction rise and fall, unresolved storyline consequences, new generation creation, and visible current-state reconstruction.

## World File Model

Suggested top-level structure:

```text
rulesets/
  classic_xianxia/
    cultivation.yaml
    breakthroughs.yaml
    events.yaml
    materialization.yaml
    content/
      spells/
      techniques/
      equipment/
      consumables/
      talismans/
      status_effects/
worlds/
  xuanyuan/
    world.yaml
    indexes/
      entities.yaml
      active_subjects.yaml
      unresolved_hooks.yaml
      timeline.yaml
    continents/
    subjects/
    storylines/
    events/
scripts/
```

Rulesets are reusable. A world save declares which ruleset it uses:

```yaml
id: world-xuanyuan
name: Xuanyuan Realm
ruleset: classic_xianxia
```

The same ruleset can run multiple worlds. World data stores current time, active subject, materialized entities, events, history, relationships, and knowledge. Ruleset data stores shared cultivation physics, breakthrough logic, content definitions, status effects, and combat content.

Character files store true state, cultivation state, resources, skills, subjective knowledge, relationships, and event history.

Event files store causality: who acted, where, when, what really happened, who saw it, what changed, and what hooks remain.

Relationship scene files store stable interaction contexts such as same-room residence, master-disciple relation, squad membership, debt, rivalry, or shared facility work. Relationships are not assumed to be symmetric.

Indexes store entities that exist by name but are not yet materialized.

## Cultivation Levels And Lifespan

The first version uses a familiar realm structure:

```text
Mortal -> Qi Refining -> Foundation Establishment -> Golden Core -> Nascent Soul -> Soul Transformation -> Void Refining -> Body Integration -> Mahayana -> Tribulation
```

Qi Refining uses layers. Later realms use early, middle, late, and perfection stages.

Lifespan is part of the world pressure. Low-level cultivators die within ordinary or slightly extended lifetimes; high-level cultivators can survive across frozen-region returns and preserve old causal chains.

## Cultivation Growth

Cultivation uses CP, or cultivation points, as the result unit. CP is not an automatic clock.

CP is produced by effective behavior:

- daily breathing and circulation practice
- ten-day seclusion
- pill refinement
- combat review
- instruction
- inheritance digestion
- opportunity events

The general formula is:

```text
CP gained = effective behavior x talent efficiency x environment efficiency x state modifier
```

Spiritual roots follow an element-root model rather than a generic quality ladder. Common roots include five-element roots, four-element roots, three-element roots, dual-element roots, single-element heavenly roots, mutated roots, and hidden/special roots. More roots usually mean slower cultivation but broader basic spell compatibility. Heavenly and mutated roots cultivate faster and are stronger with matching spells, but their usable spell families are narrower.

Most people do not continuously cultivate effectively. Every character has a cultivation state:

- not cultivating
- occasional cultivation
- stable cultivation
- key cultivation target
- seclusion push
- bottleneck stagnation
- path severed

Bottlenecks prevent the whole world from auto-leveling. A character may have enough time but lack resources, later techniques, a safe environment, health, lifespan, social freedom, or opportunity.

## Pills

Pills are concrete actions, not passive monthly bonuses. A pill must be obtained, consumed, refined, and absorbed.

Example first-version values:

- inferior qi-gathering pill: 10 CP, 2 days, high pill poison
- ordinary qi-gathering pill: 20 CP, 3 days, low pill poison
- superior qi-gathering pill: 50 CP, 5 days, repeated use restriction
- advancement pill: 100 CP, 10 days, limited useful count per layer
- foundation pill: breakthrough support, not ordinary CP

Overuse causes pill poison, resistance, unstable foundation, breakthrough penalties, and social risk.

## Breakthroughs

Small-stage breakthroughs are deterministic:

```text
CP full + no hard bottleneck + acceptable state = breakthrough
```

Large-realm breakthroughs are probabilistic. CP full only grants eligibility. Breakthrough success depends on resources, spiritual environment, technique fit, foundation, mental state, protection, wounds, pill poison, age pressure, and forced-attempt penalties.

The first Foundation Establishment template:

- base success: 20%
- foundation pill: +35%
- superior foundation pill: +45%
- spiritual cave or good site: +5% to +15%
- complete matching technique: +10%
- solid foundation: +5% to +10%
- stable mental state: +5% to +10%
- elder protection: +5% to +10%
- visible pill poison: -10% to -30%
- hidden wound or severe wound: -10% to -40%
- old age pressure: -5% to -20%
- forced breakthrough: -20% to -50%

Success rates are capped at 95% and floored at 5%. Failure consumes resources and produces real consequences: light injury, severe injury, foundation damage, realm drop, lifespan loss, madness, death, or mutation depending on failure severity.

## Skills And Techniques

Skills use SP, or skill points, with non-linear stage thresholds.

Suggested cumulative thresholds:

- unlearned: 0
- entry: 100
- practiced: 400
- proficient: 1200
- mastered: 3200
- perfected: 8200

Skill learning requires a source:

- main technique inheritance
- sect library exchange
- teacher instruction
- market purchase
- battlefield spoils
- secret realm inheritance
- observation and imitation
- self-creation or modification

Every learned skill records source, completeness, variant, SP, and stage. Completeness matters: complete, incomplete, erroneous, improved, or forbidden versions change ceiling and risk.

Ordinary practice becomes less useful at higher skill stages. Real combat, instruction, inheritance, insight, and life-or-death use matter more after proficiency.

## Combat And Objective Resolution

Combat, competitions, injuries, and high-risk contests require an objective resolver.

The LLM chooses or proposes actions based on character motives, knowledge, fear, arrogance, goals, and hidden cards. The battle resolver calculates effects from character attributes, spells, equipment, consumables, status effects, environment, and chosen actions.

Characters have calculable combat attributes such as:

- mana maximum and current mana
- life state
- divine sense
- attack
- defense
- speed
- control resistance
- poison resistance
- combat experience

Attributes come from realm, technique, skill proficiency, equipment, wounds, pills, talismans, environment, and temporary status.

Combat is resolved in rounds. A round can represent seconds or moments depending on intensity. Actions include attack spell, defense spell, movement, magic item use, talisman use, pill use, escape, observation, charging, formation setup, or surrender.

The resolver outputs hit results, damage, mana consumption, status effects, injury level, equipment triggers, and loss of action. The LLM then narrates the result and writes event consequences without overriding the calculated outcome arbitrarily.

## Content Rule Library

Objective combat requires data files for world physics.

Content types:

- spells
- techniques
- equipment
- consumables
- talismans
- status effects

Example spell fields:

```yaml
id: spell-fireball-1
name: Fireball
grade: first-rank lower
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
  proficient:
    damage_multiplier: 1.15
    mana_cost_multiplier: 0.9
  mastered:
    damage_multiplier: 1.3
    cast_speed_modifier: 1
```

The first content set should be small and support outer-sect play:

- spells: fireball, golden blade, water shield, earth armor, wind step, entangling vine, spirit eye
- consumables: qi-gathering pill, healing pill, mana recovery pill, antidote
- talismans: fireball talisman, protection talisman, escape talisman
- equipment: low-grade flying sword, ironwood shield, protective jade, storage bag
- statuses: light wound, medium wound, severe wound, poison, burn, mana exhaustion, divine-sense wound, pill poison, unstable foundation

## Competitions And Rewards

Competitions are structured event chains using the battle resolver.

A sect competition defines entry restrictions, banned tools, victory conditions, referee rules, rewards, injury handling, ranking consequences, exposure risk, and faction attention.

Rewards are not only items. They may include contribution points, sect reputation, library access, cave allocation, teacher attention, faction recruitment, grudges, or hidden suppression.

## Event System

Events are the smallest durable unit of world change.

Event types:

- daily
- social
- opportunity
- crisis
- faction
- mainline
- competition or dungeon-like event chain

Each important event records:

- real event
- visible record
- participants
- state changes
- knowledge changes
- resources consumed or gained
- injuries
- relationship changes
- unresolved hooks

An event with no state impact is narration, not an official world event.

## Mainlines And Dungeon-Like Event Chains

A mainline is a long causal chain, not a mandatory quest. It can exist without the subject, be misunderstood, missed, worsened, or partially changed.

A dungeon-like event is a bounded multi-stage event container: secret realm, sect trial, tournament, beast nest, escort task, auction, ancient cave, or ruin. It has entry conditions, time window, participants, risk pool, reward pool, rules, stages, and aftermath.

High rewards require matching risk, rarity, conversion time, and future consequences.

## Scripts

Scripts support the world but do not replace LLM judgment.

Useful first-version scripts:

- validate-world: YAML validity, missing fields, broken references, impossible state
- new-entity: create templates for character, sect, facility, event, relation scene
- calc-cultivation: calculate CP, time, pill poison, side effects
- calc-breakthrough: calculate large-realm success rate
- calc-skill: calculate SP progression and stage
- resolve-combat: calculate combat rounds from actions and content data
- scan-hooks: list unresolved causal hooks
- freeze-region: freeze a distant region
- thaw-region: prepare return progression checklist

Scripts output calculations, warnings, and structured results. The LLM writes narrative events and state updates based on those results. The developer may intervene when the LLM mishandles causality or stability.

Validation commands should take both a world save and ruleset root:

```bash
world-engine validate worlds/xuanyuan --rulesets-root rulesets
```

## First Implementation Scope

The first playable scope should be one active subject in one materialized outer-sect environment:

- one continent index
- one local cultivation region
- one sect
- one residence scene
- one facility such as pill hall
- five to ten characters
- minimal cultivation and breakthrough rules
- minimal content library
- basic event files
- validation, cultivation calculation, breakthrough calculation, skill calculation, and combat resolution scripts

This scope is enough to test whether the world can remember, evolve, fight, reward, injure, form relationships, freeze, and return without expanding into an unmanageable world tree.
