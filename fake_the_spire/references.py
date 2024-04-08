import toml
import random
from pathlib import Path
from config import config


class EnemyReference:
    _instance = None

    @staticmethod
    def get_instance():
        if EnemyReference._instance is None:
            EnemyReference._instance = EnemyReference(config.ENEMY_TOML)
        return EnemyReference._instance

    def __init__(self, enemy_toml: Path, reset: bool = False):
        if EnemyReference._instance is not None:
            if reset:
                EnemyReference._instance.all_enemies = toml.load(enemy_toml)
            else:
                raise Exception("This class is a singleton!")
        self.all_enemies = toml.load(enemy_toml)

    def generate_enemies_for_floor(self, floor_num: int) -> dict:
        enemies = []
        for enemy_name, enemy in self.all_enemies['enemies'].items():
            enemy = enemy.copy()
            if floor_num in enemy['valid_floors']:
                enemy['id'] = enemy_name
                enemy['optional_dict'] = {}
                enemies.append(enemy)
        return random.choice(enemies)

    def generate_enemies_by_id_list(self, id_list: list[str]) -> list[dict]:
        all_enemies = []
        for enemy_id in id_list:
            enemy_copy = self.all_enemies['enemies'][enemy_id].copy()
            enemy_copy['id'] = enemy_id
            enemy_copy['optional_dict'] = {}
            all_enemies.append(enemy_copy)
        return all_enemies


class CardReference:
    _instance = None

    @staticmethod
    def get_instance():
        if CardReference._instance is None:
            CardReference._instance = CardReference(config.CARD_TOML)
        return CardReference._instance

    def __init__(self, card_toml: Path, reset: bool = False):
        if CardReference._instance is not None:
            if reset:
                CardReference._instance.all_enemies = toml.load(card_toml)
            else:
                raise Exception("This class is a singleton!")
        self.all_cards = toml.load(card_toml)

    def generate_deck_dict_from_init_dict(self, init_dict: dict) -> dict:
        cards = {}
        for key, value in init_dict.items():
            card_instance = self.all_cards['cards'][key].copy()
            for i in range(value):
                card_id = f'{key}_{i}'
                cards[card_id] = card_instance
        return cards
