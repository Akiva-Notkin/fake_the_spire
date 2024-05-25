import os
from pathlib import Path


class Config:
    CARD_TOML = Path('../data/cards.toml')
    if not CARD_TOML.exists():
        CARD_TOML = Path('../../data/cards.toml')

    ENEMY_TOML = Path('../data/enemies.toml')
    if not ENEMY_TOML.exists():
        ENEMY_TOML = Path('../../data/enemies.toml')

    POTION_TOML = Path('../data/potions.toml')
    if not POTION_TOML.exists():
        POTION_TOML = Path('../../data/potions.toml')

    RELIC_TOML = Path('../data/relics.toml')
    if not RELIC_TOML.exists():
        RELIC_TOML = Path('../../data/relics.toml')

    COMBAT_TOML = Path('../data/combats.toml')
    if not COMBAT_TOML.exists():
        COMBAT_TOML = Path('../../data/combats.toml')

    POTION_REWARD_CHANGE = .1

    UNKNOWN_ROOM_HALLWAY_CHANGE = .1
    UNKNOWN_ROOM_SHOP_CHANGE = .03
    UNKNOWN_ROOM_TREASURE_CHANGE = .02

    SHOP_BASE_CARD_RARITY_DISTRIBUTION = {'rare': .09, 'uncommon': .37, 'common': .54}
    ELITE_BASE_CARD_RARITY_DISTRIBUTION = {'rare': .1, 'uncommon': .4, 'common': .5}
    HALLWAY_BASE_CARD_RARITY_DISTRIBUTION = {'rare': .03, 'uncommon': .37, 'common': .6}
    BOSS_BASE_CARD_RARITY_DISTRIBUTION = {'rare': 1., 'uncommon': 0., 'common': 0.}

    POTION_RARITY_DISTRIBUTION = {'rare': .1, 'uncommon': .25, 'common': .65}

    RELIC_RARITY_DISTRIBUTION = {'rare': .17, 'uncommon': .33, 'common': .5}

    SHOP_CARD_PRICE_VARIANCE = .1
    SHOP_CARD_PRICE_DICT = {'rare': 150, 'uncommon': 75, 'common': 50, 'base': 50, 'curse': 0}
    SHOP_COLORLESS_CARD_PREMIUM = 1.2
    SHOP_ASCENSION_CARD_PREMIUM = 1.1

    SHOP_RELIC_PRICE_VARIANCE = .05
    SHOP_RELIC_PRICE_DICT = {'rare': 300, 'uncommon': 250, 'common': 150, 'shop': 150, 'base': 150}

    SHOP_POTION_PRICE_VARIANCE = .05
    SHOP_POTION_PRICE_DICT = {'rare': 100, 'uncommon': 75, 'common': 50}

    SHOP_BASE_REMOVAL_PRICE = 75
    SHOP_COST_INCREASE_PER_REMOVAL = 25

    HALLWAY_ENCOUNTER_GOLD_DROP = 15
    ELITE_ENCOUNTER_GOLD_DROP = 30
    BOSS_ENCOUNTER_GOLD_DROP = 100
    ENCOUNTER_GOLD_DROP_VARIANCE = 5

    CHEST_SIZE_PROBABILITY_WEIGHT_DICT = {'small': 3, 'medium': 2, 'large': 1}
    CHEST_RELIC_RARITY_PROBABILITY_DICT = {'small': {'common': .75, 'uncommon': .25, 'rare': 0.},
                                           'medium': {'common': .35, 'rare': .50, 'uncommon': .15},
                                           'large': {'common': 0., 'rare': .75, 'uncommon': .25}}
    CHEST_GOLD_CHANCE_DICT = {'small': .5, 'medium': .35, 'large': .5}
    CHEST_GOLD_AMOUNT_DICT = {'small': 25, 'medium': 50, 'large': 75}
    CHEST_GOLD_VARIANCE = .1


config = Config()
