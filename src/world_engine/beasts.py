from __future__ import annotations

from pathlib import Path
from typing import Any

from world_engine.io import WorldDataError, load_yaml


def load_beast_template(ruleset_path: Path, beast_id: str) -> dict[str, Any]:
    content_root = ruleset_path / "content" / "beasts"
    if not content_root.exists():
        raise WorldDataError(f"beast content directory does not exist: {content_root}")

    for path in content_root.rglob("*.yaml"):
        data = load_yaml(path)
        if data.get("id") == beast_id:
            return data

    raise WorldDataError(f"beast template does not exist: {beast_id}")


ROLL_KEYS = (
    "life_multiplier",
    "mana_multiplier",
    "attack_multiplier",
    "defense_multiplier",
    "speed_multiplier",
)


def generate_beast_instance(
    *,
    template: dict[str, Any],
    instance_id: str,
    variant: str,
    layer: int,
    location: str,
    seed: str,
    rolls: dict[str, float],
    growth_state: dict[str, str],
) -> dict[str, Any]:
    variants = template.get("variants", {})
    if not isinstance(variants, dict) or variant not in variants:
        raise ValueError(f"unknown beast variant: {variant}")

    variant_data = variants[variant]
    if not isinstance(variant_data, dict):
        raise ValueError(f"beast variant must be a mapping: {variant}")

    layer_min, layer_max = _layer_range(variant, variant_data)
    if layer < layer_min or layer > layer_max:
        raise ValueError(f"layer {layer} is outside variant {variant} range: {layer_min}-{layer_max}")

    _validate_rolls(rolls)
    combat = _scaled_combat(template, variant_data, layer, rolls)
    return {
        "id": instance_id,
        "template": template["id"],
        "variant": variant,
        "realm": template["realm_band"],
        "layer": layer,
        "state": "alive",
        "location": location,
        "generation": {
            "method": "template_variant_roll",
            "seed": seed,
            "rolls": dict(rolls),
        },
        "combat": combat,
        "conditions": [],
        "growth_state": dict(growth_state),
        "growth_history": [],
        "material_state": {
            "corpse_condition": None,
            "harvested": [],
        },
        "event_history": [],
    }


def _layer_range(variant: str, variant_data: dict[str, Any]) -> tuple[int, int]:
    value = variant_data.get("layer_range")
    if (
        not isinstance(value, list)
        or len(value) != 2
        or not isinstance(value[0], int)
        or not isinstance(value[1], int)
    ):
        raise ValueError(f"variant {variant} must define layer_range as two integers")
    return value[0], value[1]


def _validate_rolls(rolls: dict[str, float]) -> None:
    for key in ROLL_KEYS:
        value = rolls.get(key)
        if not isinstance(value, int | float):
            raise ValueError(f"missing beast generation roll: {key}")
        if value < 0.9 or value > 1.1:
            raise ValueError(f"beast generation roll {key} out of range: {value}")


def _scaled_combat(
    template: dict[str, Any],
    variant_data: dict[str, Any],
    layer: int,
    rolls: dict[str, float],
) -> dict[str, int]:
    base_combat = template["base_combat"]
    layer_1 = base_combat["layer_1"]
    scaling = base_combat["layer_scaling"]
    variant_multipliers = variant_data.get("stat_multipliers", {})

    def scaled(stat: str, roll_key: str | None = None) -> int:
        base = int(layer_1[stat]) + int(scaling.get(stat, 0)) * (layer - 1)
        variant_multiplier = float(variant_multipliers.get(stat, 1.0))
        roll_multiplier = float(rolls.get(roll_key or f"{stat}_multiplier", 1.0))
        return round(base * variant_multiplier * roll_multiplier)

    mana_max = scaled("mana_max", "mana_multiplier")
    return {
        "mana_max": mana_max,
        "mana_current": mana_max,
        "life": scaled("life", "life_multiplier"),
        "attack": scaled("attack", "attack_multiplier"),
        "defense": scaled("defense", "defense_multiplier"),
        "speed": scaled("speed", "speed_multiplier"),
        "divine_sense": scaled("divine_sense", None),
        "control_resistance": scaled("control_resistance", None),
        "poison_resistance": scaled("poison_resistance", None),
    }
