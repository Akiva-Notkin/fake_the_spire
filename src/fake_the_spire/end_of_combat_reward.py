import logging
import random

from fake_the_spire import FloorOver
from fake_the_spire.floor import Floor
from fake_the_spire.references import CardReference, PotionReference, RelicReference

from fake_the_spire.config import config

logger = logging.getLogger('flask_app')


class EndOfCombatReward(Floor):
    def __init__(self, game_state: dict, combat_type: str, potion_rewards: list[str] = None,
                 card_rewards: list[str] = None, relic_rewards: list[str] = None):
        super().__init__(game_state)
        self.floor_type = "end_of_combat_reward"
        self.rewards_dict = self.generate_base_reward_dict(combat_type, potion_rewards, card_rewards, relic_rewards)

    def generate_base_reward_dict(self, combat_type: str, potion_rewards: list[str] = None,
                                  relic_rewards: list[str] = None, card_rewards: list[str] = None) -> dict:
        rewards_dict = {"cards": card_rewards if card_rewards else self.get_card_rewards()}
        should_get_potion = random.random() < self.game_state['environment_modifiers']['potion_reward_chance']

        if should_get_potion or potion_rewards or 'white_beast_statue' in self.game_state['player']['relics']:
            rewards_dict['potions'] = potion_rewards if potion_rewards else self.get_potion_rewards()
            self.game_state['environment_modifiers']['potion_reward_chance'] -= config.POTION_REWARD_CHANGE
        else:
            self.game_state['environment_modifiers']['potion_reward_chance'] += config.POTION_REWARD_CHANGE

        if combat_type.lower() == 'elite':
            rewards_dict['relics'] = relic_rewards if relic_rewards else self.get_relic_rewards()
        return rewards_dict

    def get_new_options(self) -> (list[str], int):
        super().get_new_options()
        options = []
        for action_type, reward_list in self.rewards_dict.items():
            for reward in reward_list:
                options.append(f"{action_type} {reward}")
        options.append('end')
        return options, 1

    def remove_from_current_floor(self, removal_type: str, removal_key: str):
        del self.rewards_dict[removal_type]

    def to_dict(self):
        return {'rewards': self.rewards_dict}

    @staticmethod
    def get_card_rewards() -> list[str]:
        card_reference = CardReference.get_instance()
        card_rewards = [card_reference.get_random_card()[0] for _ in range(3)]

        return card_rewards

    @staticmethod
    def get_potion_rewards() -> list[str]:
        potion_reference = PotionReference.get_instance()
        potion_rewards = [potion_reference.get_random_potion()[0] for _ in range(1)]
        return potion_rewards

    @staticmethod
    def get_relic_rewards() -> list[str]:
        relic_reference = RelicReference.get_instance()
        relic_rewards = [relic_reference.get_random_relic()[0] for _ in range(1)]
        return relic_rewards
