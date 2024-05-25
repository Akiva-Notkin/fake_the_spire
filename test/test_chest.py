import unittest
import logging
import random

from fake_the_spire.chest import Chest
from fake_the_spire import FloorOver

logging.basicConfig(level=logging.INFO)


class TestChest(unittest.TestCase):
    def test_get_relic_from_chest(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "gold": 1000,
                "relics": []
            },
            "environment_modifiers": {
                "potion_reward_chance": 0.4,
                'card_reward_offset': -5,
                'unknown_room_probability_dict':
                    {'hallway': .1, 'treasure': .02, 'shop': .03}
            }
        }
        chest = Chest(game_state)
        relic_to_choose = chest.chest["relics"][0]
        chest.take_action(f'relics {relic_to_choose}')
        last_underscore_index = relic_to_choose.rfind('_')
        relic_to_choose = relic_to_choose[:last_underscore_index]
        self.assertIn(relic_to_choose, game_state['player']['relics'])

    def test_take_gold(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "gold": 0,
                "relics": []
            },
            "environment_modifiers": {
                "potion_reward_chance": 0.4,
                'card_reward_offset': -5,
                'unknown_room_probability_dict':
                    {'hallway': .1, 'treasure': .02, 'shop': .03}
            }
        }
        chest = Chest(game_state)
        gold = chest.chest["gold"]
        while gold == 0:
            chest = Chest(game_state)
            gold = chest.chest["gold"]
        chest.take_action(f'gold {gold}')
        self.assertEqual(gold, game_state['player']['gold'])

