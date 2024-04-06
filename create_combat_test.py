import logging

from combat import Combat, CombatOver


class CombatActions:
    def __init__(self, player: dict, enemy_list: list[dict], on_combat_start: list[str], return_deck: dict,
                 metadata: dict = None):
        self.combat = Combat(player, enemy_list, on_combat_start, return_deck, metadata)

    def request_input_loop(self):
        try:
            while True:
                self.player_turn()
                self.enemy_turn()
        except CombatOver:
            pass

    def player_turn(self):
        logging.info(f'Player: {self.combat.player}')
        logging.info(f'Enemies: {self.combat.enemy_list}')
        player_choices = self.combat.player_choices()
        player_choices.append('end')
        logging.info(f'Player choices: {player_choices}')
        choice = input('Choose an choice: ')
        while choice not in player_choices:
            logging.info('Invalid action')
            choice = input('Choose an choice: ')
        if choice == 'end':
            return
        if 'self' in self.combat.player['hand'][choice]['target']:
            self.combat.take_action(f'play {choice}', self.combat.player, self.combat.player)
        elif 'enemy' in self.combat.player['hand'][choice]['target']:
            enemy_choices = self.combat.enemy_choices()
            logging.info(f'Enemy choices: {enemy_choices}')
            enemy_choice = input('Choose an enemy: ')
            while enemy_choice not in enemy_choices:
                logging.info('Invalid action')
                enemy_choice = input('Choose an enemy: ')
            self.combat.take_action(f'play {choice}', self.combat.player, self.combat.get_enemy(enemy_choice))

    def enemy_turn(self):
        self.combat.enemy_action()

player = {'hp': 10, 'max_hp': 10, 'optional_dict': {}}
enemy = {'hp': 10, 'max_hp': 10, 'optional_dict': {}}
deck = {'card_1': {'type': 'attack', 'actions': ['attack 5'], 'energy_cost': 0, 'target': 'enemy'},
        'card_2': {'type': 'skill', 'actions': ['apply block 5'], 'energy_cost': 0, 'target': 'self'},
         'card_3': {'type': 'skill', 'actions': ['apply weak 1'], 'energy_cost': 1, 'target': 'enemy'}}