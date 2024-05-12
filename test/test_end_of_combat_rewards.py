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
            }
        }

        end_of_combat_reward = EndOfCombatReward(game_state, combat_type='hallway')
        random_card_option = end_of_combat_reward.rewards_dict['cards'][0]
        end_of_combat_reward.take_action(f"cards {random_card_option}")
        self.assertIn(random_card_option, game_state['player']['deck'].keys())

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
                "potions": ['fake_potion'],
                "max_potions": 2
            },
            "environment_modifiers": {
                "potion_reward_chance": 1,
            }
        }

        end_of_combat_reward = EndOfCombatReward(game_state, combat_type='hallway')
        random_potion_option = end_of_combat_reward.rewards_dict['potions'][0]
        end_of_combat_reward.take_action(f"potions {random_potion_option}")
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
            }
        }

        end_of_combat_reward = EndOfCombatReward(game_state, combat_type='hallway')
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
            }
        }
        end_of_combat_reward = EndOfCombatReward(game_state, combat_type='elite')
        relic_name = end_of_combat_reward.rewards_dict['relics'][0]
        end_of_combat_reward.take_action(f"relics {relic_name}")
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
                "potions": ['fake_potion', 'fake_potion'],
                "max_potions": 2,
                "relics": []
            },
            "environment_modifiers": {
                "potion_reward_chance": 1,
            }
        }
        end_of_combat_reward = EndOfCombatReward(game_state, combat_type='hallway')
        potion_name = end_of_combat_reward.rewards_dict['potions'][0]
        end_of_combat_reward.take_action(f"potions {potion_name}")
        self.assertIn(potion_name, game_state['player']['potions'])
        self.assertNotIn("end", end_of_combat_reward.get_new_options())
        end_of_combat_reward.take_action(f"drop fake_potion")
        self.assertIn(potion_name, game_state['player']['potions'])
        self.assertEqual(len(game_state['player']['potions']), 2)

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
                "potions": ['fake_potion', 'fake_potion'],
                "max_potions": 2,
                "relics": ['white_beast_statue']
            },
            "environment_modifiers": {
                "potion_reward_chance": 0,
            }
        }
        end_of_combat_reward = EndOfCombatReward(game_state, combat_type='hallway')
        potion_name = end_of_combat_reward.rewards_dict['potions'][0]
        end_of_combat_reward.take_action(f"potions {potion_name}")
        self.assertIn(potion_name, game_state['player']['potions'])

