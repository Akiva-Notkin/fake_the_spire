import unittest
import logging

from fake_the_spire.game import GameOver, FloorOver
from fake_the_spire.combat import Combat

logging.basicConfig(level=logging.INFO)


class TestCombat(unittest.TestCase):
    # def test_apply_block_play_defend(self):
    #     game_state = {
    #         "floor_num": 1,
    #         "act": 1,
    #         "player": {
    #             "deck": {
    #                 "defend": 5
    #             },
    #             "hp": 5,
    #             "max_energy": 3,
    #             "max_hp": 5
    #         }
    #     }
    #     combat = Combat(game_state)
    #     combat.take_action("play defend_0")
    #     self.assertEqual(combat.player['optional_dict']['block'], 5)

    def test_deal_damage_play_strike(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "strike": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": []
            }
        }
        combat = Combat(game_state, ['louse'])
        combat.take_action(f"play strike_0 louse_0")
        self.assertEqual(combat.enemy_list[0]['hp'], 94)

    def test_add_vuln_deal_damage_play_bash(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "bash": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": []
            }
        }
        combat = Combat(game_state, ['louse'])
        combat.take_action(f"play bash_0 louse_0")
        self.assertEqual(combat.enemy_list[0]['hp'], 92)
        self.assertEqual(combat.enemy_list[0]['optional_dict']['vulnerable'], 2)

    def test_strike_vuln_target(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "bash": 3,
                    "strike": 2
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": []
            }
        }
        combat = Combat(game_state, ['louse'])
        combat.take_action("play bash_0 louse_0")
        combat.take_action("play strike_0 louse_0")
        self.assertEqual(combat.enemy_list[0]['hp'], 83)
        self.assertEqual(combat.enemy_list[0]['optional_dict']['vulnerable'], 2)

    def test_draw_no_deck(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "draw_two": 5,
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": []
            }
        }
        combat = Combat(game_state, ['louse'])
        combat.take_action("play draw_two_0")
        self.assertEqual(len(combat.player['hand']), 4)

    def test_end_turn_enemy_take_action(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "bash": 3,
                    "strike": 2
                },
                "hp": 10,
                "max_energy": 3,
                "max_hp": 10,
                "potions": []
            }
        }
        combat = Combat(game_state, ['louse'])
        combat.take_action("end")
        self.assertEqual(game_state['player']['hp'], 5)

    def test_attack_blocked_target(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "strike": 5
                },
                "hp": 10,
                "max_energy": 3,
                "max_hp": 10,
                "potions": []
            }
        }
        combat = Combat(game_state, ['blockman'])
        combat.take_action("end")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['block'], 10)
        combat.take_action("play strike_0 blockman_0")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['block'], 4)
        combat.take_action("play strike_1 blockman_0")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['block'], 0)
        self.assertEqual(combat.enemy_list[0]['hp'], 8)

    def test_enemy_attacks_player_with_block(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "defend": 5
                },
                "hp": 10,
                "max_energy": 3,
                "max_hp": 10,
                "potions": []
            }
        }
        combat = Combat(game_state, ['louse'])
        combat.take_action("play defend_0")
        self.assertEqual(combat.player['optional_dict']['block'], 5)
        combat.take_action("end")
        self.assertEqual(combat.player['optional_dict']['block'], 0)
        self.assertEqual(game_state['player']['hp'], 10)

    def test_enemy_with_block_and_vulnerable(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "bash": 5
                },
                "hp": 10,
                "max_energy": 3,
                "max_hp": 10,
                "potions": []
            }
        }
        combat = Combat(game_state, ['blockman'])
        combat.take_action("end")
        combat.take_action("play bash_0 blockman_0")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['block'], 2)
        self.assertEqual(combat.enemy_list[0]['optional_dict']['vulnerable'], 2)
        combat.take_action("end")
        combat.take_action("play bash_0 blockman_0")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['block'], 0)
        self.assertEqual(combat.enemy_list[0]['optional_dict']['vulnerable'], 3)
        self.assertEqual(combat.enemy_list[0]['hp'], 10)

    def test_take_combat_damage_to_0(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "bash": 3,
                    "strike": 2
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": []
            }
        }
        combat = Combat(game_state, ['louse'])
        combat.take_action("end")
        self.assertLessEqual(game_state['player']['hp'], 0)

    def test_floor_over_won_combat(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "bash": 3,
                    "strike": 2
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5,
                "potions": []
            }
        }
        combat = Combat(game_state, ['weakling'])
        with self.assertRaises(FloorOver):
            combat.take_action("play strike_0 weakling_0")
        self.assertLessEqual(combat.enemy_list[0]['hp'], 0)

    def test_small_acid_slime_combat(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "bash": 3,
                    "defend": 2
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": []
            }
        }
        combat = Combat(game_state, ['acid_slime_s'])
        self.assertTrue(combat.enemy_list[0]['intent'], 'lick')
        combat.take_action("end")
        self.assertEqual(combat.player['optional_dict']['weak'], 1)
        self.assertTrue(combat.enemy_list[0]['intent'], 'tackle')
        combat.take_action("end")
        self.assertEqual(game_state['player']['hp'], 96)
        self.assertTrue(combat.enemy_list[0]['intent'], 'lick')
        combat.take_action("end")
        self.assertEqual(combat.player['optional_dict']['weak'], 1)
        self.assertTrue(combat.enemy_list[0]['intent'], 'tackle')
        combat.take_action("end")
        self.assertEqual(game_state['player']['hp'], 92)

    def test_gremlin_nob_combat(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "defend": 5
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": []
            }
        }
        combat = Combat(game_state, ['gremlin_nob'])
        self.assertTrue(combat.enemy_list[0]['intent'], 'bellow')
        combat.take_action("end")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['enrage'], 3)
        self.assertTrue(combat.enemy_list[0]['intent'], 'skull_bash')
        combat.take_action("end")
        self.assertEqual(game_state['player']['hp'], 92)
        self.assertEqual(combat.player['optional_dict']['vulnerable'], 2)
        self.assertTrue(combat.enemy_list[0]['intent'], 'rush')
        combat.take_action("end")
        self.assertEqual(game_state['player']['hp'], 68)
        combat.take_action("play defend_0")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['strength'], 3)
        self.assertTrue(combat.enemy_list[0]['intent'], 'rush')
        combat.take_action("end")
        self.assertEqual(game_state['player']['hp'], 45)
        self.assertTrue(combat.enemy_list[0]['intent'], 'skull_bash')
