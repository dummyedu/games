from world_engine.combat import Actor, CombatAction, Spell, resolve_round


def test_attack_spell_hits_and_deals_reduced_damage():
    attacker = Actor(
        id="char-lin-xuan",
        mana=120,
        life=100,
        attack=35,
        defense=20,
        speed=25,
        hit_bonus=0,
        dodge=10,
        shield=0,
    )
    defender = Actor(
        id="char-bandit",
        mana=80,
        life=100,
        attack=25,
        defense=12,
        speed=18,
        hit_bonus=0,
        dodge=5,
        shield=0,
    )
    spell = Spell(
        id="spell-fireball-1",
        kind="attack",
        mana_cost=12,
        base_hit=70,
        base_damage=30,
        hit_modifier=0,
        damage_multiplier=1.0,
        shield=0,
        speed_bonus=0,
        dodge_bonus=0,
    )

    result = resolve_round(
        attacker,
        defender,
        CombatAction(actor_id="char-lin-xuan", spell=spell),
        hit_roll=50,
    )

    assert result.hit is True
    assert result.attacker_mana == 108
    assert result.defender_life == 82
    assert result.injury_state == "normal"


def test_defense_spell_adds_shield_without_damage():
    actor = Actor(
        id="char-lin-xuan",
        mana=120,
        life=100,
        attack=35,
        defense=20,
        speed=25,
        hit_bonus=0,
        dodge=10,
        shield=0,
    )
    defender = Actor(
        id="char-bandit",
        mana=80,
        life=100,
        attack=25,
        defense=12,
        speed=18,
        hit_bonus=0,
        dodge=5,
        shield=0,
    )
    spell = Spell(
        id="spell-water-shield-1",
        kind="defense",
        mana_cost=10,
        base_hit=100,
        base_damage=0,
        hit_modifier=0,
        damage_multiplier=1.0,
        shield=24,
        speed_bonus=0,
        dodge_bonus=0,
    )

    result = resolve_round(actor, defender, CombatAction(actor_id="char-lin-xuan", spell=spell), hit_roll=1)

    assert result.hit is True
    assert result.attacker_mana == 110
    assert result.attacker_shield == 24
    assert result.defender_life == 100
