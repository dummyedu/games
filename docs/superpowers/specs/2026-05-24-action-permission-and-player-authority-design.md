# Action Permission And Player Authority Design

Date: 2026-05-24

## Purpose

The cultivation world needs a formal boundary between player intent, author edits, and world truth. The active subject is a character inside the world, not an omnipotent editor. A player can choose what the active subject attempts, but the world engine decides whether the attempt is allowed, risky, blocked, or requires intermediate steps.

This design adds two rules:

- Player input is low-authority in-world action by default.
- World rules and objective state control outcomes unless the user explicitly switches to project/rules editing.

## Authority Model

Every user request must be interpreted in one of two modes.

### Player Mode

This is the default mode during play. The user speaks as the active subject or selects an action for the active subject.

Player-mode input can create:

- intent
- speech
- attempted movement
- attempted purchases
- attempted social requests
- attempted cultivation, training, combat, or investigation

Player-mode input cannot directly create:

- facts
- successful outcomes
- NPC decisions
- access to restricted people or places
- changes to rules, maps, inventories, identities, resources, realm, or hidden truth

Examples:

- "去集市买东西" means the subject attempts to go to the market.
- "我要见金丹老祖" means the subject attempts to seek an audience.
- "我说自己是老祖私生子" creates a claim, not a bloodline fact.
- "我捡到一件仙器" creates an attempted search or claim, not an item.

### Author Or Project Mode

This mode applies only when the user explicitly says they are changing rules, project files, world setup, or meta-design.

Examples:

- "我要追加一个世界规则"
- "修改项目，让宗门有出入限制"
- "把青岚集市加入世界设定"
- "改规则：外门弟子每月只能离宗一次"

Author/project-mode input can request edits to world rules, engine behavior, validation, or seed data. Those changes still require design and implementation discipline, but they are not interpreted as active-subject actions.

## Action Permission Outcomes

Before evolving a player-mode action, the engine should classify the action and return one of these statuses.

- `allowed`: The subject can do it now with no notable resistance.
- `allowed_with_risk`: The subject can attempt it, but time cost, danger, exposure, social pressure, or resource cost applies.
- `requires_intermediate`: The subject cannot do it directly, but there is a plausible path through procedures, favors, achievements, permissions, invitations, or escalation.
- `blocked`: Current authority, status, relationship, geography, or rule constraints forbid the action.
- `impossible_now`: The target is unreachable or undefined under current known world state, and no immediate path exists.

Narration must explain the result instead of overriding it. A blocked action may still produce consequences, such as being refused, warned, mocked, recorded, punished, or attracting attention.

## Action Rule Data

Reusable rules live in the ruleset:

```text
rulesets/classic_xianxia/actions.yaml
```

The ruleset file defines shared concepts:

- action types: `travel`, `audience`, `purchase`, `training`, `sect_procedure`, `restricted_entry`
- distance bands: `same_facility`, `same_sect`, `near_market`, `wilderness`, `remote_region`
- risk levels: `none`, `low`, `medium`, `high`, `deadly`
- authority ranks: `servant`, `outer_disciple`, `inner_disciple`, `deacon`, `elder`, `sect_master`, `ancestor`
- common blockers: `insufficient_rank`, `missing_permission`, `closed_area`, `time_pressure`, `unknown_route`, `hostile_zone`

Local rules live on world, sect, facility, or location files. Local rules override or specialize ruleset defaults.

For Qingyang Sect:

- New outer disciples must complete residence registration within three days.
- Outer disciples may make short trips to Qinglan Herb Market unless on confinement, urgent assignment, or direct order.
- Leaving soon after a rare talent confirmation creates attention and exposure risk.
- Outer disciples cannot directly meet the Golden Core ancestor without summons, elder introduction, major merit, sect emergency, or another valid escalation path.

## Resolver Interface

The first implementation should use a pure Python resolver:

```python
resolve_action_permission(subject, action, world, rules) -> ActionPermissionResult
```

Input action fields:

- `type`
- `actor_id`
- `target_id`
- `declared_intent`
- `current_place`
- `time_sensitivity`
- optional `route`, `method`, `permission_token`, or `intermediary`

Output fields:

```yaml
status: allowed | allowed_with_risk | requires_intermediate | blocked | impossible_now
reason: string
cost:
  time_days: number
  spirit_stones_low: number
risk:
  level: none | low | medium | high | deadly
  tags: []
required_steps: []
consequences: []
```

The LLM may narrate, materialize nearby entities, and write events only after the resolver returns. If the result is not `allowed`, the narrative must not pretend the action succeeded.

## Examples

### Go To Qinglan Herb Market

Subject: newly registered Qingyang outer disciple with confirmed heavenly fire root.

Expected result:

```yaml
status: allowed_with_risk
reason: Outer disciples can make short trips to the nearby market, but the subject is newly notable and has not yet settled into residence.
cost:
  time_days: 0.5
  spirit_stones_low: 0
risk:
  level: low
  tags:
    - travel
    - attention
    - market_exposure
required_steps: []
consequences:
  - The market can be materialized if the subject goes.
  - Same-batch candidates or pill-hall contacts may learn of the trip.
```

### Ask To Meet The Golden Core Ancestor

Subject: new outer disciple.

Expected result:

```yaml
status: requires_intermediate
reason: A new outer disciple has no direct audience right with the Golden Core ancestor.
cost:
  time_days: 0
  spirit_stones_low: 0
risk:
  level: low
  tags:
    - social_overreach
required_steps:
  - request advice from a deacon
  - gain elder sponsorship
  - earn major sect merit
  - receive direct summons
consequences:
  - A crude direct demand may be recorded as arrogance or ignorance.
```

### Claim A False Identity

Subject: player says "I am the ancestor's secret heir."

Expected result:

```yaml
status: allowed_with_risk
reason: The subject can make the claim, but speech does not alter bloodline truth.
risk:
  level: medium
  tags:
    - false_claim
    - sect_law
    - reputation
consequences:
  - witnesses may doubt, mock, report, or test the claim
  - law enforcement risk increases if the claim concerns high authority
```

## Validation And Tests

The implementation should add tests for:

- market travel allowed with risk for a normal outer disciple
- market travel has extra attention risk for a newly confirmed heavenly root
- direct ancestor audience requires intermediate steps
- player claims do not mutate true world state
- author-mode requests are not routed through the player action resolver
- missing local rules fall back to ruleset defaults

World validation should also check that local rule references point to known action types, rank names, and location/entity ids when those ids are materialized or indexed.

## Non-Goals

This design does not add a full UI, dynamic economy, procedural market inventory, or complete travel simulator. It only establishes the authority and action-permission boundary needed to keep play from becoming arbitrary wish fulfillment.
