import logging
import random

from fake_the_spire.floor import Floor
from fake_the_spire.references import CardReference, PotionReference, RelicReference

from fake_the_spire.config import config

logger = logging.getLogger('flask_app')


class EndOfCombatReward(Floor):
    def __init__(self, game_state: dict, combat_type: str, potion_rewards: list[str] = None,
                 card_rewards: list[str] = None, relic_rewards: list[str] = None, card_reward_count: int = None):
        super().__init__(game_state)
        self.floor_type = "end_of_combat_reward"
        self.rewards_dict = self.generate_base_reward_dict(combat_type, potion_rewards, card_rewards, relic_rewards,
                                                           card_reward_count)

    def generate_base_reward_dict(self, combat_type: str, potion_rewards: list[str] = None,
                                  relic_rewards: list[str] = None, card_rewards: list[str] = None,
                                  card_reward_count: int = None) -> dict:
        rewards_dict = self.get_card_rewards(combat_type, card_reward_count)
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
            if 'cards' in action_type:
                action_type = 'cards'
            for reward in reward_list:
                options.append(f"{action_type} {reward}")
        options.append('end')
        return options, 1

    def take_card(self, action: list[str]):
        card = action[0]
        last_underscore_index = card.rfind('_')
        card_name = card[:last_underscore_index]
        card_pack = f"cards_{card[last_underscore_index + 1:]}"
        if card_name in self.game_state['player']['deck']:
            self.game_state['player']['deck'][card_name] += 1
        else:
            self.game_state['player']['deck'][card_name] = 1
        self.remove_from_current_floor('cards', card, card_pack)

    def remove_from_current_floor(self, removal_type: str, removal_key: str, card_pack: str = None):
        if removal_type == 'cards':
            removal_type = card_pack
        del self.rewards_dict[removal_type]

    def to_dict(self):
        return {'rewards': self.rewards_dict}

    def get_card_rewards(self, combat_type: str, card_reward_count: int) -> dict:
        if combat_type == 'hallway':
            rarity_dict = config.HALLWAY_BASE_CARD_RARITY_DISTRIBUTION
        elif combat_type == 'elite':
            rarity_dict = config.ELITE_BASE_CARD_RARITY_DISTRIBUTION
        elif combat_type == 'boss':
            rarity_dict = config.BOSS_BASE_CARD_RARITY_DISTRIBUTION
        else:
            return {}

        card_rewards_dict = {}
        for i in range(card_reward_count):
            card_rewards = self.generate_distinct_reward_card_list(3, rarity_dict)
            card_reward_list = []
            for card in card_rewards:
                card_reward_list.append(f"{card[0]}_{i}")
            card_rewards_dict[f"cards_{i}"] = card_reward_list

        return card_rewards_dict

    def generate_distinct_reward_card_list(self, num_cards: int, rarity_dict: dict):
        cards = []
        card_reference = CardReference.get_instance()
        while len(cards) < num_cards:
            card = card_reference.get_random_card_by_rarity_dict_and_modifier(
                rarity_dict=rarity_dict,
                rarity_dict_modifier=self.game_state['environment_modifiers']['card_reward_offset'],
                additional_search_criteria=[('color', self.game_state['environment_modifiers']['color'])]
            )
            if card not in cards:
                cards.append(card)
                if card[1]['rarity'] == 'common':
                    self.game_state['environment_modifiers']['card_reward_offset'] += 1
                elif card[1]['rarity'] == 'rare':
                    self.game_state['environment_modifiers']['card_reward_offset'] = -5
        return cards

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
