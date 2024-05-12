
class Floor:
    def __init__(self, game_state: dict):
        self.game_state = game_state
        self.should_drop_potion = False
        self.can_remove_card = False

    def get_new_options(self) -> (list[str], int):
        options = []
        if self.should_drop_potion:
            for potion in self.game_state['player']['potions']:
                options.append(f"drop {potion}")
            return options

        if self.can_remove_card:
            for card in self.game_state['player']['deck'].keys():
                options.append(f"remove {card}")
            return options

    def to_dict(self):
        ...

    def take_action(self, action: str):
        ...

    def drop_potion(self, action: list[str]):
        potion = action[0]
        self.game_state['player']['potions'].remove(potion)
        if len(self.game_state['player']['potions']) > self.game_state['player']['max_potions']:
            self.should_drop_potion = True
        else:
            self.should_drop_potion = False

    def remove_card(self, action: list[str]):
        card_to_remove = action[0]
        for card in self.game_state['player']['deck'].keys():
            if card == card_to_remove:
                self.game_state['player']['deck'][card] -= 1
                if self.game_state['player']['deck'][card] == 0:
                    self.can_remove_card = False
                    del self.game_state['player']['deck'][card]



