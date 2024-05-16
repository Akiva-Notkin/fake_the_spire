
from fake_the_spire.floor import Floor


class Event(Floor):
    def __init__(self, game_state: dict):
        super().__init__(game_state)
        self.floor_type = "event"

    def to_dict(self):
        ...

    def take_action(self, action: str):
        ...