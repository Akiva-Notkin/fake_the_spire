import toml
import random
from pathlib import Path
from fake_the_spire.config import config


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
                CardReference._instance.all_cards = toml.load(card_toml)
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

    def get_random_card(self) -> list[str]:
        return random.choice(list(self.all_cards['cards'].keys()))


class PotionReference:
    _instance = None

    @staticmethod
    def get_instance():
        if PotionReference._instance is None:
            PotionReference._instance = PotionReference(config.POTION_TOML)
        return PotionReference._instance

    def __init__(self, potion_toml: Path, reset: bool = False):
        if PotionReference._instance is not None:
            if reset:
                PotionReference._instance.all_potions = toml.load(potion_toml)
            else:
                raise Exception("This class is a singleton!")
        self.all_potions = toml.load(potion_toml)

    def get_random_potion(self) -> list[str]:
        return random.choice(list(self.all_potions['potions'].keys()))

class RelicReference:
    _instance = None

    @staticmethod
    def get_instance():
        if RelicReference._instance is None:
            RelicReference._instance = RelicReference(config.RELIC_TOML)
        return RelicReference._instance

    def __init__(self, relic_toml: Path, reset: bool = False):
        if RelicReference._instance is not None:
            if reset:
                RelicReference._instance.all_relics = toml.load(relic_toml)
            else:
                raise Exception("This class is a singleton!")
        self.all_relics = toml.load(relic_toml)

    def get_random_relic(self) -> list[str]:
        return random.choice(list(self.all_relics['relics'].keys()))

class CombatReference:
    _instance = None

    @staticmethod
    def get_instance():
        if CombatReference._instance is None:
            CombatReference._instance = CombatReference(config.COMBAT_TOML)
        return CombatReference._instance

    def __init__(self, combat_toml: Path, reset: bool = False):
        if CombatReference._instance is not None:
            if reset:
                CombatReference._instance.all_combats = toml.load(combat_toml)
            else:
                raise Exception("This class is a singleton!")
        self.all_combats = toml.load(combat_toml)

    def generate_enemies_by_combat_type_and_act(self, act: str, combat_type: str) -> list[str]:
        valid_combats = []
        weights = []
        for combat in self.all_combats['combats'].values():
            if combat['combat_type'] == combat_type and combat['act'] == act:
                valid_combats.append(combat['enemies'])
                weights.append(combat['weight'])

        combat = random.choices(valid_combats, weights=weights)[0]
        return combat


