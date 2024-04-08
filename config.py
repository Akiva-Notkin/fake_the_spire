import os
from pathlib import Path

basedir = os.getcwd()


class Config:
    CARD_TOML = Path('data/cards.toml')
    ENEMY_TOML = Path('data/enemies.toml')


config = Config()