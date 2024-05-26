import unittest
import logging

from fake_the_spire.game import GameOver, FloorOver
from fake_the_spire.combat import Combat

logging.basicConfig(level=logging.INFO)


def get_key_by_substring(dictionary, substring):
    for key in dictionary:
        if substring in key:
            return key

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
        enemy_id = combat.enemy_list[0]['id']
        strike_id = get_key_by_substring(combat.player['hand'], 'strike')
        combat.take_action(f"play {strike_id} {enemy_id}")
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
        enemy_id = combat.enemy_list[0]['id']
        card_id = get_key_by_substring(combat.player['hand'], 'bash')
        combat.take_action(f"play {card_id} {enemy_id}")
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
        enemy_id = combat.enemy_list[0]['id']
        strike_id = get_key_by_substring(combat.player['hand'], 'strike')
        bash_id = get_key_by_substring(combat.player['hand'], 'bash')
        combat.take_action(f"play {bash_id} {enemy_id}")
        combat.take_action(f"play {strike_id} {enemy_id}")
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
        draw_two_id = get_key_by_substring(combat.player['hand'], 'draw_two')
        combat.take_action(f"play {draw_two_id}")
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
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action("end")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['block'], 10)
        strike_id = get_key_by_substring(combat.player['hand'], 'strike')
        combat.take_action(f"play {strike_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['block'], 4)
        strike_id = get_key_by_substring(combat.player['hand'], 'strike')
        combat.take_action(f"play {strike_id} {enemy_id}")
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
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id}")
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
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action("end")
        bash_id = get_key_by_substring(combat.player['hand'], 'bash')
        combat.take_action(f"play {bash_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['block'], 2)
        self.assertEqual(combat.enemy_list[0]['optional_dict']['vulnerable'], 2)
        combat.take_action("end")
        bash_id = get_key_by_substring(combat.player['hand'], 'bash')
        combat.take_action(f"play {bash_id} {enemy_id}")
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
        enemy_id = combat.enemy_list[0]['id']
        with self.assertRaises(FloorOver):
            strike_id = get_key_by_substring(combat.player['hand'], 'strike')
            combat.take_action(f"play {strike_id} {enemy_id}")
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
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['strength'], 3)
        self.assertTrue(combat.enemy_list[0]['intent'], 'rush')
        combat.take_action("end")
        self.assertEqual(game_state['player']['hp'], 45)
        self.assertTrue(combat.enemy_list[0]['intent'], 'skull_bash')

    def test_guardian_combat(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "big_ol_hammer": 4,
                    "defend": 1
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": []
            }
        }
        combat = Combat(game_state, ['the_guardian'])
        guardian_id = combat.enemy_list[0]['id']
        self.assertEqual(combat.enemy_list[0]['optional_dict']['mode_shift'], 40)
        self.assertEqual(combat.enemy_list[0]['optional_dict']['mode_shift_count'], 1)
        self.assertEqual(combat.enemy_list[0]['intent'], 'charge_up')
        big_ol_hammer_id = get_key_by_substring(combat.player['hand'], 'big_ol_hammer')
        combat.take_action(f"play {big_ol_hammer_id} {guardian_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['mode_shift'], 20)
        self.assertEqual(combat.enemy_list[0]['hp'], 230)
        combat.take_action("end")
        self.assertEqual(combat.enemy_list[0]['intent'], 'fierce_bash')
        big_ol_hammer_id = get_key_by_substring(combat.player['hand'], 'big_ol_hammer')
        combat.take_action(f"play {big_ol_hammer_id} {guardian_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['mode_shift'], 9)
        big_ol_hammer_id = get_key_by_substring(combat.player['hand'], 'big_ol_hammer')
        combat.take_action(f"play {big_ol_hammer_id} {guardian_id}")
        self.assertNotIn('mode_shift', combat.enemy_list[0]['optional_dict'])
        self.assertEqual(combat.enemy_list[0]['hp'], 199)
        self.assertEqual(combat.enemy_list[0]['stage'], 'defensive_mode')
        self.assertEqual(combat.enemy_list[0]['intent'], 'close_up')
        combat.take_action("end")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['sharp_hide'], 4)
        self.assertEqual(combat.enemy_list[0]['intent'], 'roll_attack')
        big_ol_hammer_id = get_key_by_substring(combat.player['hand'], 'big_ol_hammer')
        combat.take_action(f"play {big_ol_hammer_id} {guardian_id}")
        self.assertEqual(game_state['player']['hp'], 96)
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id} {guardian_id}")
        big_ol_hammer_id = get_key_by_substring(combat.player['hand'], 'big_ol_hammer')
        combat.take_action(f"play {big_ol_hammer_id} {guardian_id}")
        self.assertEqual(game_state['player']['hp'], 96)
        combat.take_action("end")
        self.assertEqual(combat.enemy_list[0]['intent'], 'twin_slam')
        self.assertEqual(game_state['player']['hp'], 87)
        combat.take_action("end")
        self.assertEqual(game_state['player']['hp'], 71)
        self.assertEqual(combat.enemy_list[0]['stage'], 'offensive_mode')
        self.assertEqual(combat.enemy_list[0]['intent'], 'whirlwind')
        self.assertEqual(combat.enemy_list[0]['optional_dict']['mode_shift'], 50)

    def test_load_optional_dict(self):
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
        combat = Combat(game_state, ['weakling'])
        self.assertEqual(combat.enemy_list[0]['optional_dict']['weak'], 1)