from world_engine.actions import (
    ActionPermissionResult,
    ActionRequest,
    classify_interaction_mode,
)
from pathlib import Path

from world_engine.actions import load_action_rules, resolve_action_permission


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
