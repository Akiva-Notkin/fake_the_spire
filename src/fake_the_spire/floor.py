import logging

from fake_the_spire import FloorOver

logger = logging.getLogger('flask_app')


class Floor:
    def __init__(self, game_state: dict):
        self.game_state = game_state
        self.can_remove_card = False

    def get_new_options(self) -> (list[str], int):
        options = []
        if sum(self.game_state['player']['potions'].values()) > self.game_state['player']['max_potions']:
            for potion in self.game_state['player']['potions']:
                options.append(f"drop {potion}")
            return options, 1

        if self.can_remove_card:
            for card in self.game_state['player']['deck'].keys():
                options.append(f"remove {card}")
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
        elif action[0] == 'gold':
            self.take_gold(action[1:])
        elif action[0] == 'drop':
            self.drop_potion(action[1:])
        elif action[0] == 'remove':
            self.remove_card(action[1:])
        elif action[0] == 'heal':
            self.heal(action[1:])
        elif action[0] == 'max_hp':
            self.max_hp(action[1:])
        else:
            return action

    def drop_potion(self, action: list[str]):
        potion = action[0]
        self.game_state['player']['potions'][potion] -= 1

    def remove_card(self, action: list[str]):
        card_to_remove = action[0]
        for card in self.game_state['player']['deck'].keys():
            if card == card_to_remove:
                self.game_state['player']['deck'][card] -= 1
                if self.game_state['player']['deck'][card] == 0:
                    self.can_remove_card = False
                    del self.game_state['player']['deck'][card]
                    break

    def take_relic(self, action: list[str]):
        relic = action[0]
        last_underscore_index = relic.rfind('_')
        relic_name = relic[:last_underscore_index]
        self.game_state['player']['relics'].append(relic_name)
        self.remove_from_current_floor('relics', relic)

    def take_card(self, action: list[str]):
        card = action[0]
        last_underscore_index = card.rfind('_')
        card_name = card[:last_underscore_index]
        if card_name in self.game_state['player']['deck']:
            self.game_state['player']['deck'][card_name] += 1
        else:
            self.game_state['player']['deck'][card_name] = 1
        self.remove_from_current_floor('cards', card)

    def take_potion(self, action: list[str]):
        potion = action[0]
        last_underscore_index = potion.rfind('_')
        potion_name = potion[:last_underscore_index]
        if potion_name in self.game_state['player']['potions']:
            self.game_state['player']['potions'][potion_name] += 1
        else:
            self.game_state['player']['potions'][potion_name] = 1
        self.remove_from_current_floor('potions', potion)

    def take_gold(self, action: list[str]):
        gold_amount = action[0]
        self.game_state['player']['gold'] += int(gold_amount)
        self.remove_from_current_floor('gold', gold_amount)

    def heal(self, action: list[str]):
        heal_amount = action[0]
        self.game_state['player']['hp'] += int(heal_amount)
        if self.game_state['player']['hp'] > self.game_state['player']['max_hp']:
            self.game_state['player']['hp'] = self.game_state['player']['max_hp']

    def max_hp(self, action: list[str]):
        increase_amount = int(action[0])
        self.game_state['player']['max_hp'] += increase_amount
        self.game_state['player']['hp'] += increase_amount

    def remove_from_current_floor(self, removal_type: str, removal_key: str):
        ...