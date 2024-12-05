import unittest
import logging

from fake_the_spire.end_of_combat_reward import EndOfCombatReward

logging.basicConfig(level=logging.INFO)


class TestEndOfCombatReward(unittest.TestCase):
    def test_get_card_reward(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "relics": []
            },
            "environment_modifiers": {
                "potion_reward_chance": 0.4,
                "card_reward_offset": -5,
                "color": "red"
            }
        }

        end_of_combat_reward = EndOfCombatReward(game_state, combat_type='hallway', card_reward_count=1)
        random_card_option = end_of_combat_reward.rewards_dict['cards_0'][0]
        end_of_combat_reward.take_action(f"cards {random_card_option}")
        first_dash_index = random_card_option.find('-')
        card_name = random_card_option[:first_dash_index]
        self.assertIn(card_name, game_state['player']['deck'].keys())

    def test_get_potion_reward(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": {'fake_potion': 1},
                "max_potions": 2
            },
            "environment_modifiers": {
                "potion_reward_chance": 1,
                "card_reward_offset": -5,
                "color": "red"

            }
        }

        end_of_combat_reward = EndOfCombatReward(game_state, combat_type='hallway', card_reward_count=1)
        random_potion_option = end_of_combat_reward.rewards_dict['potions'][0]
        end_of_combat_reward.take_action(f"potions {random_potion_option}")
        first_dash_index = random_potion_option.find('-')
        random_potion_option = random_potion_option[:first_dash_index]
        self.assertIn(random_potion_option, game_state['player']['potions'])

    def test_no_potion_on_0_pct_chance(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": ['fake_potion'],
                "max_potions": 2,
                "relics": []
            },
            "environment_modifiers": {
                "potion_reward_chance": 0,
                "card_reward_offset": -5,
                "color": "red"
            }
        }

        end_of_combat_reward = EndOfCombatReward(game_state, combat_type='hallway', card_reward_count=1)
        self.assertNotIn('potions', end_of_combat_reward.rewards_dict)
        self.assertEqual(.1, game_state['environment_modifiers']['potion_reward_chance'])

    def test_gain_relic(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": ['fake_potion'],
                "max_potions": 2,
                "relics": []
            },
            "environment_modifiers": {
                "potion_reward_chance": 0,
                "card_reward_offset": -5,
                "color": "red",
                "seen_relics": []
            }
        }
        end_of_combat_reward = EndOfCombatReward(game_state, combat_type='elite', card_reward_count=1)
        relic_name = end_of_combat_reward.rewards_dict['relics'][0]
        end_of_combat_reward.take_action(f"relics {relic_name}")
        first_dash_index = relic_name.find('-')
        relic_name = relic_name[:first_dash_index]
        self.assertIn(relic_name, game_state['player']['relics'])

    def test_gain_too_many_potions(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": {'block': 2},
                "max_potions": 2,
                "relics": []
            },
            "environment_modifiers": {
                "potion_reward_chance": 1,
                "card_reward_offset": -5,
                "color": "red"
            }
        }
        end_of_combat_reward = EndOfCombatReward(game_state, combat_type='hallway', card_reward_count=1)
        potion_id = end_of_combat_reward.rewards_dict['potions'][0]
        end_of_combat_reward.take_action(f"potions {potion_id}")
        first_dash_index = potion_id.find('-')
        potion_name = potion_id[:first_dash_index]
        new_options = end_of_combat_reward.get_new_options()
        self.assertIn(potion_name, game_state['player']['potions'])
        self.assertNotIn("end", new_options)
        end_of_combat_reward.take_action(f"drop {potion_name}")
        self.assertIn('block', game_state['player']['potions'])
        self.assertEqual(game_state['player']['potions']['block'], 2)

    def test_white_beast_statue(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": {'fake_potion': 2},
                "max_potions": 2,
                "relics": ['white_beast_statue']
            },
            "environment_modifiers": {
                "potion_reward_chance": 0,
                "card_reward_offset": -5,
                "color": "red"
            }
        }
        end_of_combat_reward = EndOfCombatReward(game_state, combat_type='hallway', card_reward_count=1)
        potion_name = end_of_combat_reward.rewards_dict['potions'][0]
        end_of_combat_reward.take_action(f"potions {potion_name}")
        first_dash_index = potion_name.find('-')
        potion_name = potion_name[:first_dash_index]
        self.assertIn(potion_name, game_state['player']['potions'])

    def test_multiple_card_rewards(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "relics": []
            },
            "environment_modifiers": {
                "potion_reward_chance": 0.4,
                "card_reward_offset": -5,
                "color": "red"
            }
        }
        end_of_combat_reward = EndOfCombatReward(game_state, combat_type='hallway', card_reward_count=2)
        random_card_option_0 = end_of_combat_reward.rewards_dict['cards_0'][0]
        random_card_option_1 = end_of_combat_reward.rewards_dict['cards_1'][0]
        end_of_combat_reward.take_action(f"cards {random_card_option_0}")
        end_of_combat_reward.take_action(f"cards {random_card_option_1}")
        first_dash_index_0 = random_card_option_0.find('-')
        card_name_0 = random_card_option_0[:first_dash_index_0]
        self.assertIn(card_name_0, game_state['player']['deck'].keys())
        first_dash_index_1 = random_card_option_1.find('-')
        card_name_1 = random_card_option_1[:first_dash_index_1]
        self.assertIn(card_name_1, game_state['player']['deck'].keys())


