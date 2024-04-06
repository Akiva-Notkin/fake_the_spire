import logging
import random
import toml
from pathlib import Path

ENEMY_TOML = Path('data/enemies.toml')
CARD_TOML = Path('data/cards.toml')


class FloorOver(Exception):
    pass


class GameOver(Exception):
    pass


class EnemyReference:
    _instance = None

    @staticmethod
    def get_instance(reset: bool = False):
        if EnemyReference._instance is None or reset:
            EnemyReference._instance = EnemyReference()
        return EnemyReference._instance

    def __init__(self, enemy_toml: Path = ENEMY_TOML):
        if EnemyReference._instance is not None:
            raise Exception("This class is a singleton!")
        self.all_enemies = toml.load(enemy_toml)

    def generate_enemies_for_floor(self, floor_num: int) -> dict:
        enemies = []
        for enemy_name, enemy in self.all_enemies['enemies'].items():
            if floor_num in enemy['valid_floors']:
                enemy['id'] = enemy_name
                enemy['optional_dict'] = {}
                enemies.append(enemy)
        return random.choice(enemies)


class CardReference:
    _instance = None

    @staticmethod
    def get_instance(reset: bool = False):
        if CardReference._instance is None or reset:
            CardReference._instance = CardReference()
        return CardReference._instance

    def __init__(self, card_toml: Path = CARD_TOML):
        if CardReference._instance is not None:
            raise Exception("This class is a singleton!")
        self.all_cards = toml.load(card_toml)

    def generate_deck_dict_from_init_dict(self, init_dict: dict) -> dict:
        cards = {}
        for key, value in init_dict.items():
            card_instance = self.all_cards['cards'][key]
            for i in range(value):
                card_id = f'{key}_{i}'
                cards[card_id] = card_instance
        return cards


class Game:
    def __init__(self, character: str):
        self.floor = None
        self.game_state = {'floor_num': 1, 'player':{'hp': 100, 'max_hp': 100, 'max_energy': 3,
                                                     'deck': {'strike': 5, 'bash': 1, 'defend': 4}}}
        self.current_options = []
        self.enemy_reference = EnemyReference(ENEMY_TOML)
        self.card_reference = CardReference(CARD_TOML)
        self.initialize_game()

    def initialize_game(self):
        self.floor = Combat(self.game_state)
        self.current_options = self.floor.get_new_options()

    def validate_action(self, action: str) -> bool:
        return action in self.current_options

    def action_initiate(self, action: str):
        try:
            self.floor.take_action(action)
        except FloorOver:
            self.game_state['floor_num'] += 1
            self.floor = self.get_next_floor()
            pass
        updated_options = self.floor.get_new_options()
        self.current_options = updated_options

    def get_next_floor(self):
        if self.game_state['floor_num'] > 3:
            raise GameOver
        return Combat(self.game_state)

    def to_dict(self):
        full_state = {'floor': self.floor.to_dict(), 'game_state': self.game_state}
        return full_state


class Floor:
    def __init__(self, game_state: dict):
        pass

    def get_new_options(self) -> list[str]:
        pass

    def to_dict(self):
        pass


class Combat(Floor):
    def __init__(self, game_state: dict):
        super().__init__(game_state)
        self.player = {'hp': game_state['player']['hp'], 'max_hp': game_state['player']['max_hp'],
                       'max_energy': game_state['player']['max_energy'], 'optional_dict': {}, 'hand': {}, 'energy': 0,
                       'draw_pile': self.generate_draw_pile(game_state['player']['deck']), 'discard_pile': {}}
        self.enemy_list = [self.generate_enemies(game_state['floor_num'])]
        self.combat_stack = []
        self.start_combat()

    @staticmethod
    def generate_enemies(floor_num: int) -> dict:
        enemy_reference = EnemyReference.get_instance()
        return enemy_reference.generate_enemies_for_floor(floor_num)

    @staticmethod
    def generate_draw_pile(init_deck: dict) -> dict:
        card_reference = CardReference.get_instance()
        return card_reference.generate_deck_dict_from_init_dict(init_deck)

    def to_dict(self):
        return {'player': self.player, 'enemy_list': self.enemy_list, 'combat_stack': self.combat_stack}

    def start_combat(self):
        self.start_turn()
        self.take_action()

    def take_action(self, action: str = None):
        if action:
            self.combat_stack.append(action)
        while self.combat_stack:
            action = self.combat_stack.pop()
            logging.info(f'Action: {action}')
            logging.info(f'Old state: {self.to_dict()}')
            action = action.split(' ')
            if action[0] == 'attack':
                self.attack(action[1:])
            elif action[0] == 'apply':
                self.apply(action[1:])
            elif action[0] == 'draw':
                self.draw()
            elif action[0] == 'play':
                self.play(action[1:])
            elif action[0] == 'end':
                self.resolve_end_turn()
            elif action[0] == 'gain_energy':
                self.gain_energy(action[1:])
            else:
                logging.info(f'Invalid action: {action}')

            logging.info(f'Updated state: {self.to_dict()}')
            if self.player['hp'] <= 0:
                raise GameOver
            if all(enemy['hp'] <= 0 for enemy in self.enemy_list):
                raise FloorOver

    def attack(self, action: list[str]):
        attack_value = int(action[0])
        attacker_val = action[1]
        attack_target = action[2]

        if attack_target == 'player':
            target = self.player
        else:
            target = self.get_enemy_by_id(attack_target)
        if attacker_val == 'player':
            attacker = self.player
        else:
            attacker = self.get_enemy_by_id(attacker_val)

        if 'weak' in attacker['optional_dict']:
            attack_value *= 0.75
        if 'vulnerable' in target['optional_dict']:
            attack_value *= 1.5
        if 'block' in target['optional_dict']:
            attack_value -= target['optional_dict']['block']
            if attack_value < 0:
                attack_value = 0
            if target['optional_dict']['block'] < 0:
                target['optional_dict']['block'] = 0
        target['hp'] -= attack_value

    def apply(self, action: list[str]):
        option_key = action[0]
        option_value = int(action[1])
        option_user = action[2]
        option_target = action[3]
        if option_target == 'player':
            target = self.player
        else:
            target = self.get_enemy_by_id(option_target)
        target['optional_dict'][option_key] = option_value

    def draw(self):
        if len(self.player['draw_pile']) == 0:
            self.player['draw_pile'] = self.player['discard_pile']
            self.player['discard_pile'] = {}
        random_card_id = random.choice(list(self.player['draw_pile'].keys()))
        random_card = self.player['draw_pile'].pop(random_card_id)
        self.player['hand'][random_card_id] = random_card

    def play(self, action: list[str]):
        card_id = action[0]
        card_actions = self.player['hand'][card_id]['actions']
        card_target = self.player['hand'][card_id]['target']
        if len(action) == 2:
            target_list = [self.get_enemy_by_id(action[1])]
        else:
            target_list = self.enemy_list
        for card_action in card_actions:
            if card_target == 'self':
                self.combat_stack.append(f"{card_action} player player")
            else:
                for target in target_list:
                    self.combat_stack.append(f"{card_action} player {target['id']}")

        self.combat_stack.append(f'gain_energy -{self.player["hand"][card_id]["energy_cost"]}')
        self.player['discard_pile'][card_id] = self.player['hand'][card_id]
        self.player['hand'].pop(card_id)

    def get_enemy_by_id(self, enemy_id: str) -> dict:
        for enemy in self.enemy_list:
            if enemy['id'] == enemy_id:
                return enemy
        raise KeyError(f'Enemy with id {enemy_id} not found')

    def gain_energy(self, action: list[str]):
        amount = int(action[0])
        self.player['energy'] += amount

    def get_new_options(self) -> list[str]:
        cards_in_hand = self.player['hand']
        print(cards_in_hand.keys())
        enemies = self.enemy_list
        options = []
        for card_id, card in cards_in_hand.items():
            if card['energy_cost'] <= self.player['energy']:
                if card['target'] == 'enemy':
                    for enemy in enemies:
                        enemy_id = enemy['id']
                        options.append(f'play {card_id} {enemy_id}')
                else:
                    options.append(f'play {card_id}')
        options.append('end')
        return options

    def resolve_end_turn(self):
        self.player['energy'] = 0
        self.player['discard_pile'].update(self.player['hand'])
        self.player['hand'] = {}
        for enemy in self.enemy_list:
            enemy_action = random.choice(enemy['actions'])
            self.combat_stack.append(f"{enemy_action} {enemy['id']} player")
        self.take_action()
        self.start_turn()

    def start_turn(self):
        self.combat_stack.extend(['draw'] * 5)
        self.combat_stack.append(f'gain_energy {self.player["max_energy"]}')
        self.take_action()


