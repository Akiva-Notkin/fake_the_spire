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
        self.game_state = game_state
        self.shop = self.generate_base_shop()
        self.should_drop_potion = False
        self.removed_this_shop = False

    def get_new_options(self) -> (list[str], int):
        super().get_new_options()
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
        ...

    def take_action(self, action: str):
        logger.debug(f'Action: {action}')
        logger.debug(f'Old state: {self.to_dict()}')
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
        elif action[0] == 'remove':
            self.remove_card(action[1:])
        elif action[0] == 'remove_card':
            self.remove_card_request()
        else:
            logger.info(f'Invalid action: {action}')

        logger.debug(f'Updated state: {self.to_dict()}')

    def generate_base_shop(self):
        shop = {"cards": self.generate_shop_cards() + self.generate_colorless_shop_cards(),
                "potions": self.generate_potions(),
                "relics": self.generate_relics()}
        return shop

    def generate_shop_cards(self):
        card_reference = CardReference.get_instance()
        card_options = [card_reference.get_random_card() for _ in range(3)]
        return self.give_reference_cost(card_options, rarity_to_cost_dict=config.SHOP_CARD_PRICE_DICT,
                                        cost_variance=config.SHOP_CARD_PRICE_VARIANCE)

    def generate_colorless_shop_cards(self):
        card_reference = CardReference.get_instance()
        card_options = [card_reference.get_random_card() for _ in range(2)]
        rarity_to_cost_dict = config.SHOP_CARD_PRICE_DICT.copy()
        for rarity in rarity_to_cost_dict:
            rarity_to_cost_dict[rarity] = int(rarity_to_cost_dict[rarity] * config.SHOP_COLORLESS_CARD_PREMIUM)

        return self.give_reference_cost(card_options, rarity_to_cost_dict=rarity_to_cost_dict,
                                        cost_variance=config.SHOP_CARD_PRICE_VARIANCE)

    def generate_potions(self):
        potion_reference = PotionReference.get_instance()
        potion_options = [potion_reference.get_random_potion() for _ in range(3)]
        return self.give_reference_cost(potion_options, rarity_to_cost_dict=config.SHOP_POTION_PRICE_DICT,
                                        cost_variance=config.SHOP_POTION_PRICE_VARIANCE)

    def generate_relics(self):
        relic_reference = RelicReference.get_instance()
        relic_options = [relic_reference.get_random_relic() for _ in range(3)]
        return self.give_reference_cost(relic_options, rarity_to_cost_dict=config.SHOP_RELIC_PRICE_DICT,
                                        cost_variance=config.SHOP_RELIC_PRICE_VARIANCE)

    def take_card(self, action: list[str]):
        card = action[0]
        if card in self.game_state['player']['deck']:
            self.game_state['player']['deck'][card] += 1
        else:
            self.game_state['player']['deck'][card] = 1
        self.remove_from_shop(shop_type='cards', reference_name=card)

    def take_potion(self, action: list[str]):
        potion = action[0]
        self.game_state['player']['potions'].append(potion)
        if len(self.game_state['player']['potions']) > self.game_state['player']['max_potions']:
            self.should_drop_potion = True
        else:
            self.should_drop_potion = False
        self.remove_from_shop(shop_type='potions', reference_name=potion)

    def take_relic(self, action: list[str]):
        relic = action[0]
        self.game_state['player']['relics'].append(relic)
        self.remove_from_shop(shop_type='relics', reference_name=relic)

    def remove_from_shop(self, shop_type: str, reference_name: str):
        for i in range(len(self.shop[shop_type])):
            if reference_name == self.shop[shop_type][i][0]:
                self.game_state['player']['gold'] -= self.shop[shop_type][i][1]
                del self.shop[shop_type][i]
                break

    def get_card_removal_cost(self):
        base_removal_price = config.SHOP_BASE_REMOVAL_PRICE + (config.SHOP_COST_INCREASE_PER_REMOVAL *
                                                               self.game_state['environment_modifiers']['previous_removes'])
        if 'smiling_mask' in self.game_state['player']['relics']:
            base_removal_price = 50

        return base_removal_price

    def remove_card_request(self):
        self.can_remove_card = True
        self.removed_this_shop = True
        self.game_state['player']['gold'] -= self.get_card_removal_cost()
        self.game_state['environment_modifiers']['previous_removes'] += 1

    @staticmethod
    def give_reference_cost(shop_options: list, rarity_to_cost_dict: {}, cost_variance: int):
        shop_options_with_cost = []
        for reference_name, reference_option in shop_options:
            rarity = reference_option['rarity']
            base_cost = rarity_to_cost_dict[rarity]
            int_cost_variance = math.floor(cost_variance * base_cost)
            cost = random.randint(base_cost - int_cost_variance, base_cost + int_cost_variance)
            shop_options_with_cost.append((reference_name, cost))
        return shop_options_with_cost
