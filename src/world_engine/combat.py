from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Actor:
    id: str
    mana: int
    life: int
    attack: int
    defense: int
    speed: int
    hit_bonus: int
    dodge: int
    shield: int


@dataclass(frozen=True)
class Spell:
    id: str
    kind: str
    mana_cost: int
    base_hit: int
    base_damage: int
    hit_modifier: int
    damage_multiplier: float
    shield: int
    speed_bonus: int
    dodge_bonus: int


@dataclass(frozen=True)
class CombatAction:
    actor_id: str
    spell: Spell


@dataclass(frozen=True)
class RoundResult:
    hit: bool
    attacker_mana: int
    attacker_life: int
    attacker_shield: int
    defender_life: int
    defender_shield: int
    damage: int
    injury_state: str
    notes: list[str]


def injury_state(life: int) -> str:
    if life <= 0:
        return "defeated"
    if life <= 19:
        return "near_death"
    if life <= 39:
        return "severe_wound"
    if life <= 59:
        return "medium_wound"
    if life <= 79:
        return "light_wound"
    return "normal"


def resolve_round(attacker: Actor, defender: Actor, action: CombatAction, hit_roll: int) -> RoundResult:
    if action.actor_id != attacker.id:
        raise ValueError("action actor_id must match attacker id")
    if attacker.mana < action.spell.mana_cost:
        return RoundResult(
            hit=False,
            attacker_mana=attacker.mana,
            attacker_life=attacker.life,
            attacker_shield=attacker.shield,
            defender_life=defender.life,
            defender_shield=defender.shield,
            damage=0,
            injury_state=injury_state(defender.life),
            notes=["insufficient_mana"],
        )

    attacker_mana = attacker.mana - action.spell.mana_cost
    attacker_shield = attacker.shield
    defender_life = defender.life
    defender_shield = defender.shield
    notes: list[str] = []

    if action.spell.kind == "defense":
        attacker_shield += action.spell.shield
        notes.append("shield_added")
        return RoundResult(
            hit=True,
            attacker_mana=attacker_mana,
            attacker_life=attacker.life,
            attacker_shield=attacker_shield,
            defender_life=defender_life,
            defender_shield=defender_shield,
            damage=0,
            injury_state=injury_state(defender_life),
            notes=notes,
        )

    hit_target = action.spell.base_hit + attacker.hit_bonus + action.spell.hit_modifier - defender.dodge
    hit = hit_roll <= hit_target
    damage = 0
    if hit:
        raw_damage = round(action.spell.base_damage * action.spell.damage_multiplier)
        mitigated = max(0, raw_damage - defender.defense)
        shield_absorb = min(defender_shield, mitigated)
        defender_shield -= shield_absorb
        damage = mitigated - shield_absorb
        defender_life = max(0, defender_life - damage)
        notes.append("hit")
    else:
        notes.append("miss")

    return RoundResult(
        hit=hit,
        attacker_mana=attacker_mana,
        attacker_life=attacker.life,
        attacker_shield=attacker_shield,
        defender_life=defender_life,
        defender_shield=defender_shield,
        damage=damage,
        injury_state=injury_state(defender_life),
        notes=notes,
    )
