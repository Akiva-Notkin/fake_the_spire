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


config = Config()
