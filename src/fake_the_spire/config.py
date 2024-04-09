import os
from pathlib import Path

basedir = os.getcwd()


class Config:
    CARD_TOML = Path('../data/cards.toml')
    if not CARD_TOML.exists():
        CARD_TOML = Path('../../data/cards.toml')

    ENEMY_TOML = Path('../data/enemies.toml')
    if not ENEMY_TOML.exists():
        ENEMY_TOML = Path('../../data/enemies.toml')


config = Config()