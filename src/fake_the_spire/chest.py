import random
import math

from fake_the_spire.floor import Floor
from fake_the_spire.references import RelicReference, generate_probability_list_from_probability_dict

from fake_the_spire.config import config


class Chest(Floor):
    def __init__(self, game_state: dict, chest_rarity: str = None):
        super().__init__(game_state)
        if chest_rarity is None:
            chest_rarity = self.generate_chest_rarity()
        self.chest = {'relics': [self.generate_chest_relic(chest_rarity)], 'gold': self.generate_gold(chest_rarity)}

    def take_action(self, action: str):
        super().take_action(action)

    def get_new_options(self) -> list[str]:
        options = super().get_new_options()
        if options is not None:
            return options
        options = []
        for relic in self.chest['relics']:
            options.append(f'relics {relic}')
        if self.chest["gold"]:
            options.append(f'gold {self.chest["gold"]}')
        options.append('end')
        return options

    def to_dict(self) -> dict:
        pass

    def remove_from_current_floor(self, removal_type: str, removal_key: str):
        if removal_type == 'relics':
            self.chest[removal_type].remove(removal_key)
        elif removal_type == 'gold':
            del self.chest[removal_type]

    @staticmethod
    def generate_chest_rarity():
        chest_rarity_names, weights = generate_probability_list_from_probability_dict(
            config.CHEST_SIZE_PROBABILITY_WEIGHT_DICT)
        chest_rarity = random.choices(chest_rarity_names, weights=weights)
        return chest_rarity[0]

    @staticmethod
    def generate_chest_relic(chest_rarity) -> str:
        relic_reference = RelicReference.get_instance()
        relic_rarity_dict = config.CHEST_RELIC_RARITY_PROBABILITY_DICT[chest_rarity]
        relic = relic_reference.get_single_entity_by_probability_dict('rarity', relic_rarity_dict)
        return relic[0]

    @staticmethod
    def generate_gold(chest_rarity) -> int:
        chest_gold_chance = config.CHEST_GOLD_CHANCE_DICT[chest_rarity]
        has_gold = random.random() < chest_gold_chance
        if has_gold:
            base_gold_amount = config.CHEST_GOLD_AMOUNT_DICT[chest_rarity]
            int_cost_variance = math.floor(config.CHEST_GOLD_VARIANCE * base_gold_amount)
            gold_amount = random.randint(base_gold_amount - int_cost_variance, base_gold_amount + int_cost_variance)
            return gold_amount
        return 0
