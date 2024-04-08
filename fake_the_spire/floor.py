
class Floor:
    def __init__(self, game_state: dict):
        pass

    def get_new_options(self) -> list[str]:
        ...

    def to_dict(self):
        ...

    def take_action(self, action: str):
        ...