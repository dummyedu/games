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
