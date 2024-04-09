from fake_the_spire.references import EnemyReference, CardReference
from fake_the_spire.combat import Combat
from fake_the_spire import FloorOver, GameOver

from fake_the_spire.config import config


class Game:
    def __init__(self, character: str):
        self.floor = None
        self.game_state = {'floor_num': 1, 'player': {'hp': 5, 'max_hp': 5, 'max_energy': 3,
                                                      'deck': {'strike': 5, 'bash': 1, 'defend': 4}}}
        self.current_options = []
        self.enemy_reference = EnemyReference(config.ENEMY_TOML, reset=True)
        self.card_reference = CardReference(config.CARD_TOML, reset=True)
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
        updated_options = self.floor.get_new_options()
        self.current_options = updated_options

    def get_next_floor(self):
        if self.game_state['floor_num'] > 3:
            raise GameOver(won=True)
        return Combat(self.game_state)

    def to_dict(self):
        full_state = {'floor': self.floor.to_dict(), 'game_state': self.game_state}
        return full_state
