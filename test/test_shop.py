import unittest
import logging
import random

from fake_the_spire.shop import Shop
from fake_the_spire import FloorOver

logging.basicConfig(level=logging.INFO)


class TestShop(unittest.TestCase):
    def test_buy_card(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "gold": 1000
            },
            "environment_modifiers": {
                "potion_reward_chance": 0.4,
                'card_reward_offset': -5,
                'unknown_room_probability_dict':
                    {'hallway': .1, 'treasure': .02, 'shop': .03},
                'color': 'red',
                'seen_relics': []
            }
        }

        shop = Shop(game_state)
        random_card_option, cost = shop.shop['cards'][0]
        shop.take_action(f"cards {random_card_option}")
        last_underscore_index = random_card_option.rfind('_')
        card_name = random_card_option[:last_underscore_index]
        self.assertIn(card_name, game_state['player']['deck'].keys())
        self.assertEqual(game_state['player']['gold'] + cost, 1000)

    def test_buy_potion(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": {},
                "max_potions": 2,
                "gold": 1000
            },
            "environment_modifiers": {
                "potion_reward_chance": 0.4,
                'card_reward_offset': -5,
                'unknown_room_probability_dict':
                    {'hallway': .1, 'treasure': .02, 'shop': .03},
                'color': 'red',
                'seen_relics': []

            }
        }

        shop = Shop(game_state)
        random_potion_option, cost = shop.shop['potions'][0]
        shop.take_action(f"potions {random_potion_option}")
        last_underscore_index = random_potion_option.rfind('_')
        random_potion_option = random_potion_option[:last_underscore_index]
        self.assertIn(random_potion_option, game_state['player']['potions'].keys())
        self.assertEqual(game_state['player']['gold'] + cost, 1000)

    def test_out_of_gold(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": {},
                "max_potions": 2,
                "gold": 0,
                "relics": []
            },
            "environment_modifiers": {
                "potion_reward_chance": 0.4,
                'card_reward_offset': -5,
                'unknown_room_probability_dict':
                    {'hallway': .1, 'treasure': .02, 'shop': .03},
                'previous_removes': 0,
                'color': 'red',
                'seen_relics': []

            }
        }

        shop = Shop(game_state)
        options = shop.get_new_options()
        self.assertIn('end', options)
        self.assertEqual(1, len(options))

    def test_buy_relic(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": {},
                "max_potions": 2,
                "gold": 1000,
                "relics": []
            },
            "environment_modifiers": {
                "potion_reward_chance": 0.4,
                'card_reward_offset': -5,
                'unknown_room_probability_dict':
                    {'hallway': .1, 'treasure': .02, 'shop': .03},
                'color': 'red',
                'seen_relics': []

            }
        }
        shop = Shop(game_state)
        random_relic, cost = shop.shop['relics'][0]
        shop.take_action(f"relics {random_relic}")
        last_underscore_index = random_relic.rfind('_')
        random_relic = random_relic[:last_underscore_index]
        self.assertIn(random_relic, game_state['player']['relics'])
        self.assertEqual(game_state['player']['gold'] + cost, 1000)

    def test_buy_until_empty_shop(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 1
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": {},
                "max_potions": 2,
                "gold": 10000,
                "relics": []
            },
            "environment_modifiers": {
                "potion_reward_chance": 0.4,
                'card_reward_offset': -5,
                'unknown_room_probability_dict':
                    {'hallway': .1, 'treasure': .02, 'shop': .03},
                'previous_removes': 0,
                'color': 'red',
                'seen_relics': []

            }
        }
        shop = Shop(game_state)
        options = shop.get_new_options()
        while not (len(options) == 1 and options[0] == 'end'):
            options_minus_end = [x for x in options if x != 'end']
            choice = random.choice(options_minus_end)
            shop.take_action(choice)
            options = shop.get_new_options()
        with self.assertRaises(FloorOver):
            shop.take_action('end')
        self.assertEqual(sum(game_state['player']['potions'].values()), 2)
        self.assertEqual(len(game_state['player']['relics']), 3)
        self.assertEqual(sum(game_state['player']['deck'].values()), 7)  # 7 cards in shop 1 in deck 1 removed

    def test_remove_random_card(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5,
                    "strike": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": {},
                "max_potions": 2,
                "gold": 1000,
                "relics": []
            },
            "environment_modifiers": {
                "potion_reward_chance": 0.4,
                'card_reward_offset': -5,
                'unknown_room_probability_dict':
                    {'hallway': .1, 'treasure': .02, 'shop': .03},
                'previous_removes': 0,
                'color': 'red',
                'seen_relics': []

            }
        }

        shop = Shop(game_state)
        shop.take_action("remove_card")
        random_card = random.choice(list(game_state['player']['deck'].keys()))
        shop.take_action(f"remove {random_card}")
        self.assertEqual(game_state['player']['deck'][random_card], 4)
        self.assertEqual(game_state['player']['gold'], 925)
        self.assertEqual(game_state['environment_modifiers']['previous_removes'], 1)
        new_choices = shop.get_new_options()
        self.assertNotIn('remove_card', new_choices)

    def test_remove_smiling_mask(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5,
                    "strike": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": {},
                "max_potions": 2,
                "gold": 1000,
                "relics": ['smiling_mask']
            },
            "environment_modifiers": {
                "potion_reward_chance": 0.4,
                'card_reward_offset': -5,
                'unknown_room_probability_dict':
                    {'hallway': .1, 'treasure': .02, 'shop': .03},
                'previous_removes': 0,
                'color': 'red',
                'seen_relics': []

            }
        }

        shop = Shop(game_state)
        shop.take_action("remove_card")
        random_card = random.choice(list(game_state['player']['deck'].keys()))
        shop.take_action(f"remove {random_card}")
        self.assertEqual(game_state['player']['deck'][random_card], 4)
        self.assertEqual(game_state['player']['gold'], 950)
        new_choices = shop.get_new_options()
        self.assertNotIn('remove_card', new_choices)

    def test_remove_random_previous_removes(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5,
                    "strike": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": {},
                "max_potions": 2,
                "gold": 1000,
                "relics": []
            },
            "environment_modifiers": {
                "potion_reward_chance": 0.4,
                'card_reward_offset': -5,
                'unknown_room_probability_dict':
                    {'hallway': .1, 'treasure': .02, 'shop': .03},
                'previous_removes': 3,
                'color': 'red',
                'seen_relics': []

            }
        }

        shop = Shop(game_state)
        shop.take_action("remove_card")
        random_card = random.choice(list(game_state['player']['deck'].keys()))
        shop.take_action(f"remove {random_card}")
        self.assertEqual(game_state['player']['deck'][random_card], 4)
        self.assertEqual(game_state['player']['gold'], 850)
        self.assertEqual(game_state['environment_modifiers']['previous_removes'], 4)
        new_choices = shop.get_new_options()
        self.assertNotIn('remove_card', new_choices)
