import logging
import random
import math

from fake_the_spire import FloorOver
from fake_the_spire.floor import Floor
from fake_the_spire.references import CardReference, PotionReference, RelicReference

from fake_the_spire.config import config

logger = logging.getLogger('flask_app')


class Shop(Floor):
    def __init__(self, game_state: dict):
        super().__init__(game_state)
        self.floor_type = "shop"
        self.shop = self.generate_base_shop()
        self.removed_this_shop = False

    def get_new_options(self) -> (list[str], int):
        options = super().get_new_options()
        if options is not None:
            return options
        options = []
        for action_type, shop_item_list in self.shop.items():
            for (shop_item, cost) in shop_item_list:
                if self.game_state['player']['gold'] >= cost:
                    options.append(f"{action_type} {shop_item}")
        if self.game_state['player']['gold'] >= self.get_card_removal_cost() and not self.removed_this_shop:
            options.append(f"remove_card")
        options.append('end')
        return options, 1

    def to_dict(self):
        return self.shop

    def take_action(self, action: str):
        action = super().take_action(action)
        if action is not None:
            if action[0] == 'remove_card':
                self.remove_card_request()
            else:
                logger.info(f'Invalid action: {action}')

    def generate_base_shop(self):
        shop = {"cards": self.generate_shop_cards() + self.generate_colorless_shop_cards(),
                "potions": self.generate_potions(),
                "relics": self.generate_relics()}
        return shop

    def generate_shop_cards(self):
        attack_cards = self.generate_distinct_shop_card_list('attack', 2)
        skill_cards = self.generate_distinct_shop_card_list('skill', 2)
        power_cards = self.generate_distinct_shop_card_list('power', 1)
        card_options = attack_cards + skill_cards + power_cards
        cards_with_costs = self.give_reference_cost(card_options, rarity_to_cost_dict=config.SHOP_CARD_PRICE_DICT,
                                                    cost_variance=config.SHOP_CARD_PRICE_VARIANCE)
        random_element = random.choice(cards_with_costs)
        index = cards_with_costs.index(random_element)
        cards_with_costs[index] = (random_element[0], random_element[1] // 2)
        return cards_with_costs

    def generate_distinct_shop_card_list(self, card_type: str, num_cards: int):
        cards = []
        card_reference = CardReference.get_instance()
        while len(cards) < num_cards:
            card = card_reference.get_random_card_by_rarity_dict_and_modifier(
                rarity_dict=config.SHOP_BASE_CARD_RARITY_DISTRIBUTION,
                rarity_dict_modifier=self.game_state['environment_modifiers']['card_reward_offset'],
                additional_search_criteria=[('type', card_type),
                                            ('color', self.game_state['environment_modifiers']['color'])]
            )
            if card not in cards:
                cards.append(card)
        return cards

    def generate_colorless_shop_cards(self):
        card_reference = CardReference.get_instance()
        random_rare_colorless_card = random.choice(card_reference.get_all_entities_by_search_list([("rarity", "rare"),
                                                                                                   ("color",
                                                                                                    "colorless")]))
        random_uncommon_colorless_card = random.choice(card_reference.get_all_entities_by_search_list(
            [("rarity", "uncommon"), ("color", "colorless")]
        ))

        card_options = [random_rare_colorless_card, random_uncommon_colorless_card]
        rarity_to_cost_dict = config.SHOP_CARD_PRICE_DICT.copy()
        for rarity in rarity_to_cost_dict:
            rarity_to_cost_dict[rarity] = int(rarity_to_cost_dict[rarity] * config.SHOP_COLORLESS_CARD_PREMIUM)

        return self.give_reference_cost(card_options, rarity_to_cost_dict=rarity_to_cost_dict,
                                        cost_variance=config.SHOP_CARD_PRICE_VARIANCE)

    def generate_potions(self):
        potion_reference = PotionReference.get_instance()
        potion_options = [potion_reference.get_single_entity_by_probability_dict('rarity',
                                                                                 config.POTION_RARITY_DISTRIBUTION)
                          for _ in range(3)]
        return self.give_reference_cost(potion_options, rarity_to_cost_dict=config.SHOP_POTION_PRICE_DICT,
                                        cost_variance=config.SHOP_POTION_PRICE_VARIANCE)

    def generate_relics(self):
        relic_reference = RelicReference.get_instance()
        relic_options = []
        for _ in range(2):
            relic = relic_reference.get_single_entity_by_probability_dict('rarity',
                                                                          config.RELIC_RARITY_DISTRIBUTION,
                                                                          exclude_list=
                                                                          self.game_state['environment_modifiers'][
                                                                              'seen_relics'])
            relic_options.append(relic)
            self.game_state['environment_modifiers']['seen_relics'].append(relic[1]['name'])

        shop_relic_option = random.choice(relic_reference.get_all_entities_by_search_list([('rarity', 'shop')],
                                                                                          exclude_list=
                                                                                          self.game_state[
                                                                                              'environment_modifiers'][
                                                                                              'seen_relics']))
        self.game_state['environment_modifiers']['seen_relics'].append(shop_relic_option[1]['name'])

        relic_options.append(shop_relic_option)
        return self.give_reference_cost(relic_options, rarity_to_cost_dict=config.SHOP_RELIC_PRICE_DICT,
                                        cost_variance=config.SHOP_RELIC_PRICE_VARIANCE)

    def remove_from_current_floor(self, shop_type: str, reference_name: str):
        for i in range(len(self.shop[shop_type])):
            if reference_name == self.shop[shop_type][i][0]:
                self.game_state['player']['gold'] -= self.shop[shop_type][i][1]
                del self.shop[shop_type][i]
                break

    def get_card_removal_cost(self):
        base_removal_price = config.SHOP_BASE_REMOVAL_PRICE + (config.SHOP_COST_INCREASE_PER_REMOVAL *
                                                               self.game_state['environment_modifiers'][
                                                                   'previous_removes'])
        if 'smiling_mask' in self.game_state['player']['relics']:
            base_removal_price = 50

        return base_removal_price

    def remove_card_request(self):
        self.can_remove_card = True
        self.removed_this_shop = True
        self.game_state['player']['gold'] -= self.get_card_removal_cost()
        self.game_state['environment_modifiers']['previous_removes'] += 1

    @staticmethod
    def give_reference_cost(shop_options: list, rarity_to_cost_dict: {}, cost_variance: float):
        shop_options_with_cost = []
        for reference_name, reference_option in shop_options:
            rarity = reference_option['rarity']
            base_cost = math.floor(rarity_to_cost_dict[rarity] * config.SHOP_ASCENSION_CARD_PREMIUM)
            int_cost_variance = math.floor(cost_variance * base_cost)
            cost = random.randint(base_cost - int_cost_variance, base_cost + int_cost_variance)
            shop_options_with_cost.append((reference_name, cost))
        return shop_options_with_cost
