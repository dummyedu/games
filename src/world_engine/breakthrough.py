from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BreakthroughCheck:
    base_success: int
    positive_modifiers: list[int]
    negative_modifiers: list[int]
    cap: int = 95
    floor: int = 5


def calculate_success_rate(check: BreakthroughCheck) -> int:
    raw = check.base_success + sum(check.positive_modifiers) - sum(
        abs(x) for x in check.negative_modifiers
    )
    return max(check.floor, min(check.cap, raw))


def classify_failure(success_rate: int, roll: int) -> str:
    if roll <= success_rate:
        return "success"
    over_by = roll - success_rate
    if over_by <= 20:
        return "light"
    if over_by <= 50:
        return "medium"
    return "severe"
