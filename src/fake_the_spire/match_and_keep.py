import random
import itertools

from fake_the_spire.floor import Floor
from fake_the_spire import FloorOver

class MatchAndKeep(Floor):
    def __init__(self):
        self.cards = self.generate_cards()
        self.remaining_moves = 5
        self.matches = []
        self.revealed_cards = [None] * len(self.cards)

    def generate_cards(self):
        """
        Generates a list of cards for the game.
        """
        # Replace this with your own implementation
        cards = ['A', 'B', 'C', 'D', 'E', 'F'] * 2
        random.shuffle(cards)
        return cards

    def take_action(self, action):
        """
        Takes a string representation of two card indices or IDs to flip over.
        """
        card1, card2 = map(int, action.split())
        if self.cards[card1] == self.cards[card2]:
            self.matches.append(self.cards[card1])
            self.remaining_moves -= 1
            self.revealed_cards[card1] = self.cards[card1]
            self.revealed_cards[card2] = self.cards[card2]
        else:
            self.remaining_moves -= 1

    def get_new_options(self):
        """
        Returns a list of all possible combinations of two card indices.
        """
        unmatched_indices = [i for i, card in enumerate(self.cards) if card not in self.matches]
        options = list(itertools.combinations(unmatched_indices, 2))
        return [f"{i} {j}" for i, j in options]

    def to_dict(self):
        """
        Returns a dictionary representing the current state of the game.
        """
        return {
            'remaining_moves': self.remaining_moves,
            'matches': self.matches,
            'revealed_cards': [str(card) for card in self.revealed_cards]
        }