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
