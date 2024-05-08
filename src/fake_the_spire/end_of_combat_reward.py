import logging
import random

from fake_the_spire import FloorOver
from fake_the_spire.floor import Floor
from fake_the_spire.references import CardReference, PotionReference, RelicReference

from fake_the_spire.config import config


class EndOfCombatReward(Floor):
    def __init__(self, game_state: dict, combat_type: str, potion_rewards: list[str] = None,
                 card_rewards: list[str] = None, relic_rewards: list[str] = None):
        super().__init__(game_state)
        self.floor_type = "end_of_combat_reward"
        self.rewards_dict = self.generate_base_reward_dict(combat_type, potion_rewards, card_rewards, relic_rewards)
        self.should_drop_potion = False

    def generate_base_reward_dict(self, combat_type: str, potion_rewards: list[str] = None,
                                  relic_rewards: list[str] = None, card_rewards: list[str] = None) -> dict:
        rewards_dict = {"cards": card_rewards if card_rewards else self.get_card_rewards()}
        should_get_potion = random.random() < self.game_state['potion_reward_chance']

        if should_get_potion or potion_rewards:
            rewards_dict['potions'] = potion_rewards if potion_rewards else self.get_potion_rewards()
            self.game_state['potion_reward_chance'] -= config.POTION_REWARD_CHANGE
        else:
            self.game_state['potion_reward_chance'] += config.POTION_REWARD_CHANGE

        if combat_type.lower() == 'elite':
            rewards_dict['relics'] = relic_rewards if relic_rewards else self.get_relic_rewards()
        return rewards_dict

    def get_new_options(self) -> (list[str], int):
        options = []
        if self.should_drop_potion:
            for potion in self.game_state['player']['potions']:
                options.append(f"drop {potion}")
        else:
            for action_type, reward_list in self.rewards_dict.items():
                for reward in reward_list:
                    options.append(f"{action_type} {reward}")
            options.append('end')
        return options, 1

    def take_action(self, action: str):
        logging.debug(f'Action: {action}')
        logging.debug(f'Old state: {self.to_dict()}')
        action = action.split(' ')
        if action[0] == 'end':
            raise FloorOver
        elif action[0] == 'cards':
            self.take_card(action[1:])
        elif action[0] == 'potions':
            self.take_potion(action[1:])
        elif action[0] == 'relics':
            self.take_relic(action[1:])
        elif action[0] == 'drop':
            self.drop_potion(action[1:])

    def take_card(self, action: list[str]):
        card = action[0]
        if card in self.game_state['player']['deck']:
            self.game_state['player']['deck'][card] += 1
        else:
            self.game_state['player']['deck'][card] = 1
        del self.rewards_dict['cards']

    def take_potion(self, action: list[str]):
        potion = action[0]
        self.game_state['player']['potions'].append(potion)
        if len(self.game_state['player']['potions']) > self.game_state['player']['max_potions']:
            self.should_drop_potion = True
        else:
            self.should_drop_potion = False
        del self.rewards_dict['potions']

    def take_relic(self, action: list[str]):
        relic = action[0]
        self.game_state['player']['relics'].append(relic)
        del self.rewards_dict['relics']

    def drop_potion(self, action: list[str]):
        potion = action[0]
        self.game_state['player']['potions'].remove(potion)
        if len(self.game_state['player']['potions']) > self.game_state['player']['max_potions']:
            self.should_drop_potion = True
        else:
            self.should_drop_potion = False

    def to_dict(self):
        return {'rewards': self.rewards_dict}

    @staticmethod
    def get_card_rewards() -> list[str]:
        card_reference = CardReference.get_instance()
        card_rewards = [card_reference.get_random_card() for _ in range(3)]
        return card_rewards

    @staticmethod
    def get_potion_rewards() -> list[str]:
        potion_reference = PotionReference.get_instance()
        potion_rewards = [potion_reference.get_random_potion() for _ in range(1)]
        return potion_rewards

    @staticmethod
    def get_relic_rewards() -> list[str]:
        relic_reference = RelicReference.get_instance()
        relic_rewards = [relic_reference.get_random_relic() for _ in range(1)]
        return relic_rewards
