# Action Permission And Player Authority Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a rules-backed action permission resolver so player input becomes attempted in-world action, while explicit project/rule edits remain author-mode requests.

**Architecture:** Add a focused `world_engine.actions` module for authority classification, action request/result dataclasses, rule loading, and permission resolution. Add reusable action concepts to `rulesets/classic_xianxia/actions.yaml`, local Qingyang access rules to the sect file, and validation checks so local rule references stay consistent with the ruleset and entity index.

**Tech Stack:** Python 3.12, dataclasses, pathlib, PyYAML via existing `world_engine.io`, pytest, YAML world/ruleset files.

---

## Scope Boundary

This plan implements the approved spec at `docs/superpowers/specs/2026-05-24-action-permission-and-player-authority-design.md`.

Included:

- Player vs author/project authority classification.
- Structured action request/result types.
- Reusable ruleset action concepts.
- Local Qingyang sect action permissions for market travel and ancestor audience.
- Resolver behavior for market travel, ancestor audience, unsupported actions, and speech claims.
- Validation for action rule references.
- Tests covering the approved examples.

Excluded:

- Full UI.
- Dynamic market economy.
- Procedural inventory generation.
- Complete travel simulation.
- Automatic LLM orchestration.

## File Map

- Create: `src/world_engine/actions.py` - action dataclasses, authority classification, rule loading, and resolver.
- Create: `tests/test_actions.py` - unit tests for classifier and resolver outcomes.
- Modify: `src/world_engine/validation.py` - validate action ruleset and local rule references.
- Modify: `tests/test_validation.py` - validation coverage for action rules.
- Create: `rulesets/classic_xianxia/actions.yaml` - shared action types, distance bands, risk levels, authority ranks, blockers.
- Modify: `worlds/qinglan_frontier/continents/eastern_wilds/materialized/qinglan_frontier/sects/qingyang/sect.yaml` - Qingyang local permission rules.

## Task 1: Add Action Types And Authority Classifier

**Files:**
- Create: `src/world_engine/actions.py`
- Test: `tests/test_actions.py`

- [ ] **Step 1: Write failing classifier and dataclass tests**

Create `tests/test_actions.py`:

```python
from world_engine.actions import (
    ActionPermissionResult,
    ActionRequest,
    classify_interaction_mode,
)


def test_classify_player_mode_by_default():
    assert classify_interaction_mode("我要去集市买东西") == "player"
    assert classify_interaction_mode("我要见金丹老祖") == "player"
    assert classify_interaction_mode("我说自己是老祖私生子") == "player"


def test_classify_author_project_mode_when_user_explicitly_edits_rules_or_project():
    assert classify_interaction_mode("我要追加一个世界规则") == "author_project"
    assert classify_interaction_mode("修改项目，让宗门有出入限制") == "author_project"
    assert classify_interaction_mode("改设定：外门弟子每月只能离宗一次") == "author_project"
    assert classify_interaction_mode("change the rules so outer disciples need travel passes") == "author_project"


def test_action_request_and_result_to_dict_are_stable():
    request = ActionRequest(
        type="travel",
        actor_id="char-active-subject",
        target_id="qinglan-herb-market",
        declared_intent="去集市买东西",
        current_place="facility-qingyang-outer-affairs-hall",
        time_sensitivity="normal",
    )
    assert request.to_dict() == {
        "type": "travel",
        "actor_id": "char-active-subject",
        "target_id": "qinglan-herb-market",
        "declared_intent": "去集市买东西",
        "current_place": "facility-qingyang-outer-affairs-hall",
        "time_sensitivity": "normal",
        "route": None,
        "method": None,
        "permission_token": None,
        "intermediary": None,
    }

    result = ActionPermissionResult(
        status="allowed_with_risk",
        reason="Outer disciples can make short market trips.",
        cost={"time_days": 0.5, "spirit_stones_low": 0},
        risk={"level": "low", "tags": ["travel"]},
        required_steps=[],
        consequences=["The market can be materialized."],
    )
    assert result.to_dict() == {
        "status": "allowed_with_risk",
        "reason": "Outer disciples can make short market trips.",
        "cost": {"time_days": 0.5, "spirit_stones_low": 0},
        "risk": {"level": "low", "tags": ["travel"]},
        "required_steps": [],
        "consequences": ["The market can be materialized."],
    }
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_actions.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'world_engine.actions'`.

- [ ] **Step 3: Implement action dataclasses and authority classifier**

Create `src/world_engine/actions.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from world_engine.io import load_yaml


AUTHOR_PROJECT_MARKERS = (
    "追加一个世界规则",
    "修改世界规则",
    "修改规则",
    "修改项目",
    "改设定",
    "author mode",
    "project mode",
    "change the rules",
    "edit the rules",
    "modify the project",
    "world setup",
)


@dataclass(frozen=True)
class ActionRequest:
    type: str
    actor_id: str
    target_id: str
    declared_intent: str
    current_place: str
    time_sensitivity: str = "normal"
    route: str | None = None
    method: str | None = None
    permission_token: str | None = None
    intermediary: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "type": self.type,
            "actor_id": self.actor_id,
            "target_id": self.target_id,
            "declared_intent": self.declared_intent,
            "current_place": self.current_place,
            "time_sensitivity": self.time_sensitivity,
            "route": self.route,
            "method": self.method,
            "permission_token": self.permission_token,
            "intermediary": self.intermediary,
        }


@dataclass(frozen=True)
class ActionPermissionResult:
    status: str
    reason: str
    cost: dict[str, float | int]
    risk: dict[str, object]
    required_steps: list[str]
    consequences: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "reason": self.reason,
            "cost": dict(self.cost),
            "risk": dict(self.risk),
            "required_steps": list(self.required_steps),
            "consequences": list(self.consequences),
        }


def classify_interaction_mode(user_text: str) -> str:
    normalized = user_text.strip().lower()
    if any(marker in normalized for marker in AUTHOR_PROJECT_MARKERS):
        return "author_project"
    return "player"
```

- [ ] **Step 4: Run tests to verify they pass**

Run:

```bash
.venv/bin/python -m pytest tests/test_actions.py -q
```

Expected: PASS with `3 passed`.

- [ ] **Step 5: Commit**

Run:

```bash
git add src/world_engine/actions.py tests/test_actions.py
git commit -m "feat: add action authority primitives"
```

Expected: commit succeeds.

## Task 2: Add Ruleset And Qingyang Local Permission Data

**Files:**
- Create: `rulesets/classic_xianxia/actions.yaml`
- Modify: `worlds/qinglan_frontier/continents/eastern_wilds/materialized/qinglan_frontier/sects/qingyang/sect.yaml`
- Test: `tests/test_actions.py`

- [ ] **Step 1: Add failing rule-loading test**

Append to `tests/test_actions.py`:

```python
from pathlib import Path

from world_engine.actions import load_action_rules


def test_load_action_rules_reads_ruleset_and_local_sect_rules():
    rules = load_action_rules(Path("worlds/qinglan_frontier"))

    assert "travel" in rules["action_types"]
    assert "near_market" in rules["distance_bands"]
    assert "outer_disciple" in rules["authority_ranks"]
    assert rules["local_rules"]["sect-qingyang"]["market_travel"]["target"] == "qinglan-herb-market"
    assert (
        rules["local_rules"]["sect-qingyang"]["ancestor_audience"]["target_rank"]
        == "ancestor"
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
.venv/bin/python -m pytest tests/test_actions.py::test_load_action_rules_reads_ruleset_and_local_sect_rules -q
```

Expected: FAIL with `ImportError` for `load_action_rules` or a missing `actions.yaml` error after the function exists.

- [ ] **Step 3: Create ruleset action data**

Create `rulesets/classic_xianxia/actions.yaml`:

```yaml
id: rules-actions-v1
action_types:
  - travel
  - audience
  - purchase
  - training
  - sect_procedure
  - restricted_entry
  - speech_claim
distance_bands:
  same_facility:
    base_time_days: 0
    base_risk: none
  same_sect:
    base_time_days: 0.1
    base_risk: none
  near_market:
    base_time_days: 0.5
    base_risk: low
  wilderness:
    base_time_days: 1
    base_risk: medium
  remote_region:
    base_time_days: 10
    base_risk: high
risk_levels:
  - none
  - low
  - medium
  - high
  - deadly
authority_ranks:
  - servant
  - outer_disciple
  - inner_disciple
  - deacon
  - elder
  - sect_master
  - ancestor
common_blockers:
  - insufficient_rank
  - missing_permission
  - closed_area
  - time_pressure
  - unknown_route
  - hostile_zone
outcomes:
  - allowed
  - allowed_with_risk
  - requires_intermediate
  - blocked
  - impossible_now
```

- [ ] **Step 4: Add Qingyang local permission rules**

Modify `worlds/qinglan_frontier/continents/eastern_wilds/materialized/qinglan_frontier/sects/qingyang/sect.yaml` by adding this block after `rules:`:

```yaml
action_rules:
  market_travel:
    type: travel
    target: qinglan-herb-market
    minimum_rank: outer_disciple
    distance_band: near_market
    status: allowed_with_risk
    base_reason: Outer disciples can make short trips to Qinglan Herb Market unless confined, assigned urgent duty, or directly ordered to remain.
    risk_tags:
      - travel
      - market_exposure
    extra_risk_if:
      newly_confirmed_heavenly_root:
        risk_level: low
        tags:
          - attention
        reason: The subject was just confirmed as a heavenly fire root and may be noticed outside the sect.
  ancestor_audience:
    type: audience
    target_rank: ancestor
    minimum_rank: elder
    status: requires_intermediate
    base_reason: A new outer disciple has no direct audience right with the Golden Core ancestor.
    risk_level: low
    risk_tags:
      - social_overreach
    required_steps:
      - request advice from a deacon
      - gain elder sponsorship
      - earn major sect merit
      - receive direct summons
```

Keep the existing `rules:` values intact.

- [ ] **Step 5: Implement rule loading**

Extend `src/world_engine/actions.py` with these imports and functions:

```python
def load_action_rules(world_root: Path, rulesets_root: Path | None = None) -> dict[str, Any]:
    world = load_yaml(world_root / "world.yaml")
    ruleset = world.get("ruleset")
    if not isinstance(ruleset, str):
        raise ValueError(f"world has no ruleset: {world_root}")

    root = rulesets_root or _default_rulesets_root(world_root)
    ruleset_rules = load_yaml(root / ruleset / "actions.yaml")
    local_rules = _load_local_action_rules(world_root)
    return {
        "action_types": _as_list(ruleset_rules.get("action_types")),
        "distance_bands": _as_mapping(ruleset_rules.get("distance_bands")),
        "risk_levels": _as_list(ruleset_rules.get("risk_levels")),
        "authority_ranks": _as_list(ruleset_rules.get("authority_ranks")),
        "common_blockers": _as_list(ruleset_rules.get("common_blockers")),
        "outcomes": _as_list(ruleset_rules.get("outcomes")),
        "local_rules": local_rules,
    }


def _default_rulesets_root(world_root: Path) -> Path:
    if world_root.parent.name == "worlds":
        return world_root.parent.parent / "rulesets"
    return world_root.parent / "rulesets"


def _load_local_action_rules(world_root: Path) -> dict[str, dict[str, Any]]:
    local_rules: dict[str, dict[str, Any]] = {}
    for path in world_root.rglob("*.yaml"):
        data = load_yaml(path)
        entity_id = data.get("id")
        action_rules = data.get("action_rules")
        if isinstance(entity_id, str) and isinstance(action_rules, dict):
            local_rules[entity_id] = action_rules
    return local_rules


def _as_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _as_mapping(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {str(key): item for key, item in value.items()}
```

- [ ] **Step 6: Run rule loading test**

Run:

```bash
.venv/bin/python -m pytest tests/test_actions.py::test_load_action_rules_reads_ruleset_and_local_sect_rules -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

Run:

```bash
git add src/world_engine/actions.py tests/test_actions.py rulesets/classic_xianxia/actions.yaml worlds/qinglan_frontier/continents/eastern_wilds/materialized/qinglan_frontier/sects/qingyang/sect.yaml
git commit -m "feat: add action permission rule data"
```

Expected: commit succeeds.

## Task 3: Resolve Market Travel And Ancestor Audience

**Files:**
- Modify: `src/world_engine/actions.py`
- Test: `tests/test_actions.py`

- [ ] **Step 1: Add failing resolver tests**

Append to `tests/test_actions.py`:

```python
from world_engine.actions import resolve_action_permission


def test_market_travel_for_new_heavenly_root_outer_disciple_is_allowed_with_attention_risk():
    rules = load_action_rules(Path("worlds/qinglan_frontier"))
    subject = {
        "id": "char-active-subject",
        "identity": {"current_status": "outer_disciple"},
        "true_state": {"spiritual_root": "single_element_heavenly_root"},
        "knowledge": {
            "known_facts": [
                "The formal retest confirmed a single-element heavenly fire root."
            ]
        },
    }
    request = ActionRequest(
        type="travel",
        actor_id="char-active-subject",
        target_id="qinglan-herb-market",
        declared_intent="去集市买东西",
        current_place="facility-qingyang-outer-affairs-hall",
    )

    result = resolve_action_permission(subject, request, rules)

    assert result.status == "allowed_with_risk"
    assert result.cost == {"time_days": 0.5, "spirit_stones_low": 0}
    assert result.risk["level"] == "low"
    assert result.risk["tags"] == ["travel", "market_exposure", "attention"]
    assert "newly notable" in result.reason
    assert "market can be materialized" in result.consequences[0]


def test_direct_ancestor_audience_requires_intermediate_steps():
    rules = load_action_rules(Path("worlds/qinglan_frontier"))
    subject = {
        "id": "char-active-subject",
        "identity": {"current_status": "outer_disciple"},
        "true_state": {"spiritual_root": "single_element_heavenly_root"},
        "knowledge": {"known_facts": []},
    }
    request = ActionRequest(
        type="audience",
        actor_id="char-active-subject",
        target_id="sect-qingyang-golden-core-ancestor",
        declared_intent="我要见金丹老祖",
        current_place="facility-qingyang-outer-affairs-hall",
    )

    result = resolve_action_permission(subject, request, rules)

    assert result.status == "requires_intermediate"
    assert result.risk == {"level": "low", "tags": ["social_overreach"]}
    assert result.required_steps == [
        "request advice from a deacon",
        "gain elder sponsorship",
        "earn major sect merit",
        "receive direct summons",
    ]
    assert "no direct audience right" in result.reason
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_actions.py::test_market_travel_for_new_heavenly_root_outer_disciple_is_allowed_with_attention_risk tests/test_actions.py::test_direct_ancestor_audience_requires_intermediate_steps -q
```

Expected: FAIL with `ImportError` for `resolve_action_permission`.

- [ ] **Step 3: Implement resolver**

Append to `src/world_engine/actions.py`:

```python
def resolve_action_permission(
    subject: dict[str, Any],
    action: ActionRequest,
    rules: dict[str, Any],
) -> ActionPermissionResult:
    if action.type == "travel" and action.target_id == "qinglan-herb-market":
        return _resolve_qinglan_market_travel(subject, rules)
    if action.type == "audience" and "ancestor" in action.target_id:
        return _resolve_ancestor_audience(rules)
    if action.type == "speech_claim":
        return ActionPermissionResult(
            status="allowed_with_risk",
            reason="The subject can make the claim, but speech does not alter world truth.",
            cost={"time_days": 0, "spirit_stones_low": 0},
            risk={"level": "medium", "tags": ["false_claim", "sect_law", "reputation"]},
            required_steps=[],
            consequences=[
                "Witnesses may doubt, mock, report, or test the claim.",
                "Law enforcement risk increases if the claim concerns high authority.",
            ],
        )
    return ActionPermissionResult(
        status="impossible_now",
        reason=f"No action permission rule is available for {action.type} targeting {action.target_id}.",
        cost={"time_days": 0, "spirit_stones_low": 0},
        risk={"level": "none", "tags": []},
        required_steps=[],
        consequences=[],
    )


def _resolve_qinglan_market_travel(
    subject: dict[str, Any],
    rules: dict[str, Any],
) -> ActionPermissionResult:
    market_rule = rules["local_rules"]["sect-qingyang"]["market_travel"]
    distance = rules["distance_bands"][market_rule["distance_band"]]
    tags = list(market_rule.get("risk_tags", []))
    reason = str(market_rule["base_reason"])

    if _is_newly_confirmed_heavenly_root(subject):
        extra = market_rule["extra_risk_if"]["newly_confirmed_heavenly_root"]
        tags.extend(extra.get("tags", []))
        reason = (
            "Outer disciples can make short market trips, but this subject is newly notable "
            "after heavenly fire root confirmation."
        )

    return ActionPermissionResult(
        status=str(market_rule["status"]),
        reason=reason,
        cost={
            "time_days": float(distance["base_time_days"]),
            "spirit_stones_low": 0,
        },
        risk={"level": str(distance["base_risk"]), "tags": tags},
        required_steps=[],
        consequences=[
            "The market can be materialized if the subject goes.",
            "Same-batch candidates or pill-hall contacts may learn of the trip.",
        ],
    )


def _resolve_ancestor_audience(rules: dict[str, Any]) -> ActionPermissionResult:
    rule = rules["local_rules"]["sect-qingyang"]["ancestor_audience"]
    return ActionPermissionResult(
        status=str(rule["status"]),
        reason=str(rule["base_reason"]),
        cost={"time_days": 0, "spirit_stones_low": 0},
        risk={"level": str(rule["risk_level"]), "tags": list(rule["risk_tags"])},
        required_steps=list(rule["required_steps"]),
        consequences=["A crude direct demand may be recorded as arrogance or ignorance."],
    )


def _is_newly_confirmed_heavenly_root(subject: dict[str, Any]) -> bool:
    true_state = subject.get("true_state", {})
    knowledge = subject.get("knowledge", {})
    known_facts = knowledge.get("known_facts", []) if isinstance(knowledge, dict) else []
    return (
        isinstance(true_state, dict)
        and true_state.get("spiritual_root") == "single_element_heavenly_root"
        and any(
            isinstance(fact, str) and "confirmed a single-element heavenly fire root" in fact
            for fact in known_facts
        )
    )
```

- [ ] **Step 4: Run resolver tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_actions.py::test_market_travel_for_new_heavenly_root_outer_disciple_is_allowed_with_attention_risk tests/test_actions.py::test_direct_ancestor_audience_requires_intermediate_steps -q
```

Expected: PASS.

- [ ] **Step 5: Run all action tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_actions.py -q
```

Expected: PASS.

- [ ] **Step 6: Commit**

Run:

```bash
git add src/world_engine/actions.py tests/test_actions.py
git commit -m "feat: resolve core player action permissions"
```

Expected: commit succeeds.

## Task 4: Ensure Player Claims Do Not Mutate Truth

**Files:**
- Modify: `tests/test_actions.py`
- Modify: `src/world_engine/actions.py`

- [ ] **Step 1: Add failing speech-claim immutability test**

Append to `tests/test_actions.py`:

```python
def test_speech_claim_is_risky_but_does_not_mutate_subject_truth():
    rules = load_action_rules(Path("worlds/qinglan_frontier"))
    subject = {
        "id": "char-active-subject",
        "identity": {"current_status": "outer_disciple"},
        "true_state": {"bloodline": "ordinary_mortal_family"},
        "knowledge": {"known_facts": []},
    }
    before = subject.copy()
    before["true_state"] = dict(subject["true_state"])
    request = ActionRequest(
        type="speech_claim",
        actor_id="char-active-subject",
        target_id="claim-ancestor-secret-heir",
        declared_intent="我说自己是老祖私生子",
        current_place="facility-qingyang-outer-affairs-hall",
    )

    result = resolve_action_permission(subject, request, rules)

    assert result.status == "allowed_with_risk"
    assert result.risk["level"] == "medium"
    assert subject == before
    assert subject["true_state"]["bloodline"] == "ordinary_mortal_family"
```

- [ ] **Step 2: Run test**

Run:

```bash
.venv/bin/python -m pytest tests/test_actions.py::test_speech_claim_is_risky_but_does_not_mutate_subject_truth -q
```

Expected: PASS if Task 3 implementation already handles speech claims without mutation. If it fails, the resolver is mutating input and must be fixed by returning results only.

- [ ] **Step 3: Commit the test**

Run:

```bash
git add tests/test_actions.py src/world_engine/actions.py
git commit -m "test: lock player claims out of truth mutation"
```

Expected: commit succeeds.

## Task 5: Validate Action Rule References

**Files:**
- Modify: `src/world_engine/validation.py`
- Modify: `tests/test_validation.py`

- [ ] **Step 1: Add failing validation tests**

Append to `tests/test_validation.py`:

```python
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
```

- [ ] **Step 2: Run validation tests to verify they fail**

Run:

```bash
.venv/bin/python -m pytest tests/test_validation.py::test_validate_world_reports_unknown_local_action_type tests/test_validation.py::test_validate_world_reports_unknown_local_rank_and_target -q
```

Expected: FAIL because validation does not inspect `action_rules`.

- [ ] **Step 3: Extend validation to collect action rule metadata**

Modify `src/world_engine/validation.py`.

Add these local variables after `spiritual_root_ids` is initialized:

```python
    action_types: set[str] | None = None
    authority_ranks: set[str] | None = None
```

Inside the `else:` block where the ruleset exists, after `spiritual_root_ids = _collect_spiritual_root_ids(ruleset_path)`, add:

```python
            action_types, authority_ranks = _collect_action_rule_ids(ruleset_path)
```

Update the `_validate_entity_ruleset_references(...)` call by adding `entities`, `action_types`, and `authority_ranks` before `errors`:

```python
                entities,
                action_types,
                authority_ranks,
                errors,
```

Update the function signature:

```python
def _validate_entity_ruleset_references(
    entity_id: str,
    entity_index: dict[str, object],
    entity_data: dict[str, object],
    content_ids: set[str] | None,
    content_by_id: dict[str, dict[str, object]],
    spiritual_root_ids: set[str] | None,
    entities: dict[str, dict[str, object]],
    action_types: set[str] | None,
    authority_ranks: set[str] | None,
    errors: list[str],
) -> None:
```

Add this helper near `_collect_spiritual_root_ids`:

```python
def _collect_action_rule_ids(ruleset_path: Path) -> tuple[set[str], set[str]]:
    path = ruleset_path / "actions.yaml"
    if not path.exists():
        return set(), set()

    try:
        data = load_yaml(path)
    except WorldDataError:
        return set(), set()

    action_types = data.get("action_types", [])
    authority_ranks = data.get("authority_ranks", [])
    return _string_set(action_types), _string_set(authority_ranks)


def _string_set(value: object) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}
```

At the end of `_validate_entity_ruleset_references`, add:

```python
    _validate_action_rules(
        entity_id,
        entity_data,
        entities,
        action_types,
        authority_ranks,
        errors,
    )
```

Add this helper:

```python
def _validate_action_rules(
    entity_id: str,
    entity_data: dict[str, object],
    entities: dict[str, dict[str, object]],
    action_types: set[str] | None,
    authority_ranks: set[str] | None,
    errors: list[str],
) -> None:
    action_rules = entity_data.get("action_rules", {})
    if not isinstance(action_rules, dict):
        return

    for rule_id, rule in action_rules.items():
        if not isinstance(rule_id, str) or not isinstance(rule, dict):
            continue

        rule_type = rule.get("type")
        if (
            action_types is not None
            and isinstance(rule_type, str)
            and rule_type not in action_types
        ):
            errors.append(
                f"entity {entity_id} action rule {rule_id} references unknown action type: {rule_type}"
            )

        minimum_rank = rule.get("minimum_rank")
        if (
            authority_ranks is not None
            and isinstance(minimum_rank, str)
            and minimum_rank not in authority_ranks
        ):
            errors.append(
                f"entity {entity_id} action rule {rule_id} references unknown authority rank: {minimum_rank}"
            )

        target = rule.get("target")
        if isinstance(target, str) and target not in entities:
            errors.append(
                f"entity {entity_id} action rule {rule_id} references unknown target: {target}"
            )
```

- [ ] **Step 4: Run targeted validation tests**

Run:

```bash
.venv/bin/python -m pytest tests/test_validation.py::test_validate_world_reports_unknown_local_action_type tests/test_validation.py::test_validate_world_reports_unknown_local_rank_and_target -q
```

Expected: PASS.

- [ ] **Step 5: Validate current worlds**

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

- [ ] **Step 6: Commit**

Run:

```bash
git add src/world_engine/validation.py tests/test_validation.py
git commit -m "feat: validate action rule references"
```

Expected: commit succeeds.

## Task 6: Add End-To-End Resolver Test With Current World Files

**Files:**
- Modify: `tests/test_actions.py`

- [ ] **Step 1: Add current-world integration test**

Append to `tests/test_actions.py`:

```python
from world_engine.io import load_yaml


def test_resolver_uses_current_world_subject_for_market_permission():
    world_root = Path("worlds/qinglan_frontier")
    subject = load_yaml(
        world_root
        / "continents/eastern_wilds/materialized/qinglan_frontier/sects/qingyang/characters/active_subject.yaml"
    )
    rules = load_action_rules(world_root)
    request = ActionRequest(
        type="travel",
        actor_id="char-active-subject",
        target_id="qinglan-herb-market",
        declared_intent="去集市买东西",
        current_place="facility-qingyang-outer-affairs-hall",
    )

    result = resolve_action_permission(subject, request, rules)

    assert result.status == "allowed_with_risk"
    assert result.risk["level"] == "low"
    assert "attention" in result.risk["tags"]
```

- [ ] **Step 2: Run integration test**

Run:

```bash
.venv/bin/python -m pytest tests/test_actions.py::test_resolver_uses_current_world_subject_for_market_permission -q
```

Expected: PASS.

- [ ] **Step 3: Commit**

Run:

```bash
git add tests/test_actions.py
git commit -m "test: cover action resolver against seed world"
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

Expected: no uncommitted implementation changes from this plan. Pre-existing uncommitted world-play changes may still appear if they were present before implementation; do not revert them.

- [ ] **Step 4: Record final implementation result**

In the final response, report:

- tests run and pass/fail result
- world validation result
- whether any pre-existing world-play changes remain uncommitted
- the key API: `resolve_action_permission(subject, action, rules)`
