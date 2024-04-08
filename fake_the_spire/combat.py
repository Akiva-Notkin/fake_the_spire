import logging
import random
from fake_the_spire import FloorOver, GameOver
from fake_the_spire.floor import Floor
from fake_the_spire.references import EnemyReference, CardReference


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
                raise GameOver(won=False)
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
            original_attack_value = attack_value
            attack_value -= target['optional_dict']['block']
            if attack_value < 0:
                attack_value = 0
            target['optional_dict']['block'] -= original_attack_value
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
        if option_key in target['optional_dict']:
            target['optional_dict'][option_key] += option_value
        else:
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


