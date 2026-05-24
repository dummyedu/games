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
