class FloorOver(Exception):
    pass


class GameOver(Exception):
    def __init__(self, won: bool = False):
        super().__init__(won)
