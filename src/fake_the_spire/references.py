import toml
import random
import uuid
from pathlib import Path
from fake_the_spire.config import config


def generate_probability_list_from_probability_dict(probability_dict: dict) -> (list, list):
    names = []
    weights = []
    for name, probability in probability_dict.items():
        names.append(name)
        weights.append(probability)
    return names, weights


class BaseReference:
    _instance = None

    def __init__(self, entity_toml: Path, entity_name: str, reset: bool = False):
        if BaseReference._instance is not None:
            if reset:
                BaseReference._instance.all_entities = toml.load(entity_toml)
            else:
                raise Exception("This class is a singleton!")
        self.all_entities = toml.load(entity_toml)[entity_name]

    def get_all_entities_by_search_list(self, search_list: list, exclude_list: list[str] = None) -> list:
        entities = []
        for (entity_name, entity_dict) in self.all_entities.items():
            if exclude_list:
                if entity_name in exclude_list:
                    continue
            if all(search_keyword in entity_dict and entity_dict[search_keyword] in search_value
                   for (search_keyword, search_value) in search_list):
                entity_dict['name'] = entity_name
                entities.append((f"{entity_name}_{uuid.uuid4()}", entity_dict))
        return entities

    def get_single_entity_by_probability_dict(self, probability_keyword: str, probability_dict: dict,
                                              exclude_list: list[str] = None) -> tuple:
        names, weights = generate_probability_list_from_probability_dict(probability_dict)
        choice = random.choices(names, weights=weights)
        potential_entities = self.get_all_entities_by_search_list([(probability_keyword, choice)], exclude_list)
        if len(potential_entities) == 0:
            return 'poop', {'name': 'poop', 'rarity': 'base'}
        return random.choice(potential_entities)


class EnemyReference(BaseReference):
    @staticmethod
    def get_instance():
        if EnemyReference._instance is None:
            EnemyReference._instance = EnemyReference(config.ENEMY_TOML, 'enemies')
        return EnemyReference._instance

    def generate_enemy_by_id(self, enemy_id: str) -> dict:
        enemy_copy = self.all_entities[enemy_id].copy()
        enemy_copy['id'] = f"{enemy_id}_{uuid.uuid4()}"
        enemy_copy['hp'] = enemy_copy['max_hp']
        if 'optional_dict' not in enemy_copy:
            enemy_copy['optional_dict'] = {}
        enemy_copy['action_history'] = []
        enemy_copy['stage'] = enemy_copy['stage_start_combat']
        return enemy_copy

    def generate_enemies_by_id_list(self, id_list: list[str]) -> list[dict]:
        all_enemies = []
        for enemy_id in id_list:
            enemy_copy = self.generate_enemy_by_id(enemy_id)
            all_enemies.append(enemy_copy)
        return all_enemies


class CardReference(BaseReference):
    @staticmethod
    def get_instance():
        if CardReference._instance is None:
            CardReference._instance = CardReference(config.CARD_TOML, 'cards')
        return CardReference._instance

    def generate_deck_dict_from_init_dict(self, init_dict: dict) -> dict:
        cards = {}
        for key, value in init_dict.items():
            card_instance = self.all_entities[key].copy()
            for i in range(value):
                card_id = f'{key}_{uuid.uuid4()}'
                cards[card_id] = card_instance
        return cards

    def get_random_card(self) -> list[str]:
        return random.choice(list(self.all_entities.items()))

    def get_random_card_by_rarity_dict_and_modifier(self, rarity_dict: dict, rarity_dict_modifier: int,
                                                    additional_search_criteria: list = None) -> dict:
        rarity_dict_pct_modifier = rarity_dict_modifier / 100
        rarity_dict_copy = rarity_dict.copy()
        if rarity_dict_copy['rare'] < 1.:
            rarity_dict_copy['common'] -= rarity_dict_pct_modifier
            rarity_dict_copy['rare'] += rarity_dict_pct_modifier
            if rarity_dict_copy['rare'] < 0:
                rarity_dict_copy['uncommon'] += rarity_dict_copy['rare']
                rarity_dict_copy['rare'] = 0.
        potential_entities = []
        while len(potential_entities) == 0:
            names, weights = generate_probability_list_from_probability_dict(rarity_dict_copy)
            choice = random.choices(names, weights=weights)[0]
            search_list = [('rarity', choice)]
            if additional_search_criteria is not None:
                search_list.extend(additional_search_criteria)
            potential_entities = self.get_all_entities_by_search_list(search_list)
            del rarity_dict_copy[choice]
        return random.choice(potential_entities)


class PotionReference(BaseReference):
    @staticmethod
    def get_instance():
        if PotionReference._instance is None:
            PotionReference._instance = PotionReference(config.POTION_TOML, 'potions')
        return PotionReference._instance

    def get_random_potion(self) -> list[str]:
        return random.choice(list(self.all_entities.items()))


class RelicReference(BaseReference):
    @staticmethod
    def get_instance():
        if RelicReference._instance is None:
            RelicReference._instance = RelicReference(config.RELIC_TOML, 'relics')
        return RelicReference._instance

    def get_random_relic(self) -> list[str]:
        return random.choice(list(self.all_entities.items()))


class CombatReference(BaseReference):

    @staticmethod
    def get_instance():
        if CombatReference._instance is None:
            CombatReference._instance = CombatReference(config.COMBAT_TOML, 'combats')
        return CombatReference._instance

    def generate_enemies_by_combat_type_and_act(self, act: str, combat_type: str) -> list[str]:
        valid_combats = []
        weights = []
        for combat in self.all_entities.values():
            if combat['combat_type'] == combat_type and combat['act'] == act:
                valid_combats.append(combat['enemies'])
                weights.append(combat['weight'])

        combat = random.choices(valid_combats, weights=weights)[0]
        return combat
