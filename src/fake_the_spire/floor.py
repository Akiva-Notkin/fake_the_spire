
class Floor:
    def __init__(self, game_state: dict):
        self.game_state = game_state

    def get_new_options(self) -> (list[str], int):
        ...

    def to_dict(self):
        ...

    def take_action(self, action: str):
        ...
