from fake_the_spire.references import EnemyReference, CardReference
from fake_the_spire.combat import Combat
from fake_the_spire.end_of_combat_reward import EndOfCombatReward
from fake_the_spire import FloorOver, GameOver

from fake_the_spire.config import config

import logging

logger = logging.getLogger('flask_app')


class Game:
    def __init__(self, character: str):
        self.floor = None
        self.game_state = {'floor_num': 1, 'act': 1,
                           'player': {'hp': 75, 'max_hp': 75, 'max_energy': 3,
                                      'deck': {'strike': 5, 'bash': 1, 'defend': 4},
                                      'potions': [], 'max_potions': 2,
                                      'relics': ['burning_blood']},
                           'potion_reward_chance': 0.4,
                           }
        self.current_options = []
        self.current_options_amount = 0
        self.enemy_reference = EnemyReference(config.ENEMY_TOML, reset=True)
        self.card_reference = CardReference(config.CARD_TOML, reset=True)
        self.initialize_game()

    def initialize_game(self):
        self.floor = Combat(self.game_state)
        self.current_options, self.current_options_amount = self.floor.get_new_options()

    def validate_action(self, action_lst: list[str]) -> bool:
        for action in action_lst:
            if action not in self.current_options:
                return False
        if len(action_lst) != self.current_options_amount:
            return False
        return True

    def action_initiate(self, action: list[str]):
        action = action[0]
        try:
            self.floor.take_action(action)
        except FloorOver:
            self.floor = self.get_next_floor()
        if self.game_state['player']['hp'] <= 0:
            raise GameOver(won=False)
        updated_options = self.floor.get_new_options()
        self.current_options, self.current_options_amount = updated_options

    def get_next_floor(self):
        if self.floor.floor_type == "combat":
            combat_type = self.floor.combat_type
            return EndOfCombatReward(self.game_state, combat_type=combat_type)

        elif self.floor.floor_type == "end_of_combat_reward":
            self.game_state['floor_num'] += 1
            if self.game_state['floor_num'] > 15:
                raise GameOver(True)
            combat_type = 'hallway'
            if self.game_state['floor_num'] % 5 == 0:
                combat_type = 'elite'
                if self.game_state['floor_num'] == 15:
                    combat_type = 'boss'
            return Combat(self.game_state, combat_type=combat_type)

    def to_dict(self):
        full_state = {'floor': self.floor.to_dict(), 'game_state': self.game_state}
        return full_state
