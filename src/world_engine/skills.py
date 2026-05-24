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
