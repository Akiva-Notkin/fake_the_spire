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
                "potions": {}
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
                "potions": {}
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
                "potions": {}
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
                "potions": {}
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
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        combat.take_action("end_turn")
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
                "potions": {}
            }
        }
        combat = Combat(game_state, ['blockman'])
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action("end_turn")
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
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 5)
        combat.take_action("end_turn")
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
                "potions": {}
            }
        }
        combat = Combat(game_state, ['blockman'])
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action("end_turn")
        bash_id = get_key_by_substring(combat.player['hand'], 'bash')
        combat.take_action(f"play {bash_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['block'], 2)
        self.assertEqual(combat.enemy_list[0]['optional_dict']['vulnerable'], 2)
        combat.take_action("end_turn")
        bash_id = get_key_by_substring(combat.player['hand'], 'bash')
        combat.take_action(f"play {bash_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['block'], 0)
        self.assertEqual(combat.enemy_list[0]['optional_dict']['vulnerable'], 3)
        self.assertEqual(combat.enemy_list[0]['hp'], 8)

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
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        combat.take_action("end_turn")
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
                "potions": {}
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
                "potions": {}
            }
        }
        combat = Combat(game_state, ['acid_slime_s'])
        self.assertTrue(combat.enemy_list[0]['intent'], 'lick')
        combat.take_action("end_turn")
        self.assertEqual(combat.player['optional_dict']['weak'], 1)
        self.assertTrue(combat.enemy_list[0]['intent'], 'tackle')
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 96)
        self.assertTrue(combat.enemy_list[0]['intent'], 'lick')
        combat.take_action("end_turn")
        self.assertEqual(combat.player['optional_dict']['weak'], 1)
        self.assertTrue(combat.enemy_list[0]['intent'], 'tackle')
        combat.take_action("end_turn")
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
                "potions": {}
            }
        }
        combat = Combat(game_state, ['gremlin_nob'])
        self.assertTrue(combat.enemy_list[0]['intent'], 'bellow')
        combat.take_action("end_turn")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['enrage'], 3)
        self.assertTrue(combat.enemy_list[0]['intent'], 'skull_bash')
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 92)
        self.assertEqual(combat.player['optional_dict']['vulnerable'], 2)
        self.assertTrue(combat.enemy_list[0]['intent'], 'rush')
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 68)
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['strength'], 3)
        self.assertTrue(combat.enemy_list[0]['intent'], 'rush')
        combat.take_action("end_turn")
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
                "potions": {}
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
        combat.take_action("end_turn")
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
        combat.take_action("end_turn")
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
        combat.take_action("end_turn")
        self.assertEqual(combat.enemy_list[0]['intent'], 'twin_slam')
        self.assertEqual(game_state['player']['hp'], 87)
        combat.take_action("end_turn")
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
                "potions": {}
            }
        }
        combat = Combat(game_state, ['weakling'])
        self.assertEqual(combat.enemy_list[0]['optional_dict']['weak'], 1)

    def test_anger(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "anger": 5
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        enemy_id = combat.enemy_list[0]['id']
        anger_id = get_key_by_substring(combat.player['hand'], 'anger')
        combat.take_action(f"play {anger_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 94)
        self.assertEqual(len(combat.player['discard_pile'].keys()), 2)

    def test_body_slam(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "defend": 2,
                    "body_slam": 3
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        enemy_id = combat.enemy_list[0]['id']
        body_slam_id = get_key_by_substring(combat.player['hand'], 'body_slam')
        combat.take_action(f"play {body_slam_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 100)
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id}")
        body_slam_id = get_key_by_substring(combat.player['hand'], 'body_slam')
        combat.take_action(f"play {body_slam_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 95)
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id}")
        body_slam_id = get_key_by_substring(combat.player['hand'], 'body_slam')
        combat.take_action(f"play {body_slam_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 85)
        self.assertEqual(combat.player['optional_dict']['block'], 10)

    def test_clash(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "defend": 1,
                    "combust": 1,
                    "strike": 1,
                    "injury": 1,
                    "clash": 1
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        enemy_id = combat.enemy_list[0]['id']
        clash_id = get_key_by_substring(combat.player['hand'], 'clash')
        self.assertNotIn(f"play {clash_id} {enemy_id}", combat.get_new_options())
        strike_id = get_key_by_substring(combat.player['hand'], 'strike')
        combat.take_action(f"play {strike_id} {enemy_id}")
        self.assertIn(f"play {clash_id} {enemy_id}", combat.get_new_options())
        combat.take_action(f"play {clash_id} {enemy_id}")
        self.assertEqual(80, combat.enemy_list[0]['hp'])

    def test_cleave(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "cleave": 5
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse', 'louse', 'louse'])
        cleave_id = get_key_by_substring(combat.player['hand'], 'cleave')
        combat.take_action(f"play {cleave_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 92)
        self.assertEqual(combat.enemy_list[1]['hp'], 92)
        self.assertEqual(combat.enemy_list[2]['hp'], 92)

    def test_clothesline(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "clothesline": 5
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        enemy_id = get_key_by_substring(combat.player['hand'], 'clothesline')
        clothesline_id = get_key_by_substring(combat.player['hand'], 'clothesline')
        combat.take_action(f"play {clothesline_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 88)
        self.assertEqual(combat.enemy_list[0]['optional_dict']['weak'], 2)

    def test_flex(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "flex": 3,
                    "strike": 2
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        enemy_id = combat.enemy_list[0]['id']
        flex_id = get_key_by_substring(combat.player['hand'], 'flex')
        combat.take_action(f"play {flex_id}")
        strike_id = get_key_by_substring(combat.player['hand'], 'strike')
        combat.take_action(f"play {strike_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 92)
        combat.take_action("end_turn")
        strike_id = get_key_by_substring(combat.player['hand'], 'strike')
        combat.take_action(f"play {strike_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 86)
        combat.take_action("end_turn")
        strike_id = get_key_by_substring(combat.player['hand'], 'strike')
        combat.take_action(f"play {strike_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 80)

    def test_headbutt(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "headbutt": 25
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        enemy_id = combat.enemy_list[0]['id']
        headbutt_id = get_key_by_substring(combat.player['hand'], 'headbutt')
        combat.take_action(f"play {headbutt_id} {enemy_id}")
        discard_id = get_key_by_substring(combat.player['discard_pile'], 'headbutt')
        headbutt_id = get_key_by_substring(combat.player['hand'], 'headbutt')
        combat.take_action(f"play {headbutt_id} {enemy_id} {discard_id}")
        self.assertIn(discard_id, combat.player['top_of_deck_ids'])
        self.assertIn(discard_id, combat.player['draw_pile'])
        self.assertNotIn(discard_id, combat.player['discard_pile'])
        combat.take_action("end_turn")
        self.assertIn(discard_id, combat.player['hand'])

    def test_heavy_blade(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "heavy_blade": 4,
                    "flex": 1
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        enemy_id = combat.enemy_list[0]['id']
        flex_id = get_key_by_substring(combat.player['hand'], 'flex')
        combat.take_action(f"play {flex_id}")
        heavy_blade_id = get_key_by_substring(combat.player['hand'], 'heavy_blade')
        combat.take_action(f"play {heavy_blade_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 80)

    def test_iron_wave(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "iron_wave": 5,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        enemy_id = combat.enemy_list[0]['id']
        iron_wave_id = get_key_by_substring(combat.player['hand'], 'iron_wave')
        combat.take_action(f"play {iron_wave_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 95)
        self.assertEqual(combat.player['optional_dict']['block'], 5)

    def test_perfected_strike(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "perfected_strike": 3,
                    "strike": 1,
                    "twin_strike": 1,
                    "pommel_strike": 1,
                    "anger": 1
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        enemy_id = combat.enemy_list[0]['id']
        perfect_strike_id = get_key_by_substring(combat.player['hand'], 'perfected_strike')
        combat.take_action(f"play {perfect_strike_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 82)

    def test_pommel_strike(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "pommel_strike": 6
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        enemy_id = combat.enemy_list[0]['id']
        pommel_strike_id = get_key_by_substring(combat.player['hand'], 'pommel_strike')
        combat.take_action(f"play {pommel_strike_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 91)
        self.assertEqual(len(combat.player['hand']), 5)

    def test_shrug_it_off(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "shrug_it_off": 6
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        enemy_id = combat.enemy_list[0]['id']
        shrug_it_off_id = get_key_by_substring(combat.player['hand'], 'shrug_it_off')
        combat.take_action(f"play {shrug_it_off_id} {enemy_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 8)
        self.assertEqual(len(combat.player['hand']), 5)

    def test_sword_boomerang(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "sword_boomerang": 5
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse', 'louse'])
        sword_boomerang_id = get_key_by_substring(combat.player['hand'], 'sword_boomerang')
        combat.take_action(f"play {sword_boomerang_id}")
        sword_boomerang_id = get_key_by_substring(combat.player['hand'], 'sword_boomerang')
        combat.take_action(f"play {sword_boomerang_id}")
        sword_boomerang_id = get_key_by_substring(combat.player['hand'], 'sword_boomerang')
        combat.take_action(f"play {sword_boomerang_id}")
        # Sometimes useful but not 100% reliable because random
        # self.assertLess(combat.enemy_list[0]['hp'], 100)
        # self.assertLess(combat.enemy_list[1]['hp'], 100)
        self.assertEqual(combat.enemy_list[0]['hp'] + combat.enemy_list[1]['hp'], 173)

    def test_thunderclap(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "thunderclap": 5
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse', 'louse', 'louse'])
        thunderclap_id = get_key_by_substring(combat.player['hand'], 'thunderclap')
        combat.take_action(f"play {thunderclap_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 96)
        self.assertEqual(combat.enemy_list[1]['hp'], 96)
        self.assertEqual(combat.enemy_list[2]['hp'], 96)
        self.assertEqual(combat.enemy_list[0]['optional_dict']['vulnerable'], 1)
        self.assertEqual(combat.enemy_list[1]['optional_dict']['vulnerable'], 1)
        self.assertEqual(combat.enemy_list[2]['optional_dict']['vulnerable'], 1)

    def test_true_grit(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "true_grit": 5,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        true_grit_id = get_key_by_substring(combat.player['hand'], 'true_grit')
        combat.take_action(f"play {true_grit_id}")
        self.assertEqual(len(combat.player['hand']), 3)
        self.assertEqual(len(combat.player['discard_pile']), 1)
        self.assertEqual(len(combat.player['exhaust_pile']), 1)
        self.assertEqual(combat.player['optional_dict']['block'], 7)

    def test_twin_strike(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "twin_strike": 4,
                    "flex": 1
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        twin_strike_id = get_key_by_substring(combat.player['hand'], 'twin_strike')
        enemy_id = combat.enemy_list[0]['id']
        flex_id = get_key_by_substring(combat.player['hand'], 'flex')
        combat.take_action(f"play {flex_id}")
        combat.take_action(f"play {twin_strike_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 86)

    def test_warcry(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "warcry": 3,
                    "strike": 2
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        warcry_id = get_key_by_substring(combat.player['hand'], 'warcry')
        strike_id = get_key_by_substring(combat.player['hand'], 'strike')
        self.assertIn(f"play {warcry_id} {strike_id}", combat.get_new_options())
        self.assertNotIn(f"play {warcry_id} {warcry_id}", combat.get_new_options())
        combat.take_action(f"play {warcry_id} {strike_id}")
        self.assertIn(strike_id, combat.player['top_of_deck_ids'])
        self.assertIn(strike_id, combat.player['draw_pile'])
        self.assertNotIn(strike_id, combat.player['hand'])
        self.assertIn(warcry_id, combat.player['exhaust_pile'])
        combat.take_action("end_turn")
        self.assertIn(strike_id, combat.player['hand'])
        self.assertIn(warcry_id, combat.player['exhaust_pile'])

    def test_wild_strike(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "wild_strike": 5
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        # Test that the player takes damage after playing wild strike
        combat = Combat(game_state, ['louse'])
        wild_strike_id = get_key_by_substring(combat.player['hand'], 'wild_strike')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play {wild_strike_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 88)
        wound_id = get_key_by_substring(combat.player['draw_pile'], 'wound')
        self.assertIn(wound_id, combat.player['draw_pile'])

    def test_battle_trance(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "battle_trance": 4,
                    "pommel_strike": 4,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        battle_trance_id = get_key_by_substring(combat.player['hand'], 'battle_trance')
        combat.take_action(f"play {battle_trance_id}")
        self.assertEqual(len(combat.player['hand']), 7)
        pommel_strike_id = get_key_by_substring(combat.player['hand'], 'pommel_strike')
        combat.take_action(f"play {pommel_strike_id} {combat.enemy_list[0]['id']}")
        self.assertEqual(len(combat.player['hand']), 6)
        combat.take_action("end_turn")
        self.assertEqual(len(combat.player['hand']), 5)
        battle_trance_id = get_key_by_substring(combat.player['hand'], 'battle_trance')
        combat.take_action(f"play {battle_trance_id}")
        self.assertEqual(len(combat.player['hand']), 7)

    def test_blood_for_blood(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "blood_for_blood": 5,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        self.assertEqual(['end_turn'], combat.get_new_options())
        combat.take_action("end_turn")
        enemy_id = combat.enemy_list[0]['id']
        blood_for_blood_id = get_key_by_substring(combat.player['hand'], 'blood_for_blood')
        self.assertIn(f"play {blood_for_blood_id} {enemy_id}", combat.get_new_options())
        combat.take_action(f"play {blood_for_blood_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 82)

    def test_bloodletting(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "bloodletting": 4,
                    "defend": 1
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }
        combat = Combat(game_state, ['louse'])
        bloodletting_id = get_key_by_substring(combat.player['hand'], 'bloodletting')
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id}")
        combat.take_action(f"play {bloodletting_id}")
        self.assertEqual(game_state['player']['hp'], 97)
        self.assertEqual(combat.player['energy'], 4)
        self.assertEqual(combat.player['optional_dict']['block'], 5)

    def test_burning_pact(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "burning_pact": 4,
                    "defend": 4,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        burning_pact_id = get_key_by_substring(combat.player['hand'], 'burning_pact')
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {burning_pact_id} {defend_id}")
        self.assertEqual(len(combat.player['hand']), 5)
        self.assertEqual(len(combat.player['discard_pile']), 1)
        self.assertEqual(len(combat.player['exhaust_pile']), 1)

    def test_carnage(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "carnage": 10
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        carnage_id = get_key_by_substring(combat.player['hand'], 'carnage')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play {carnage_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 80)
        self.assertEqual(len(combat.player['hand']), 4)
        combat.take_action("end_turn")
        self.assertEqual(len(combat.player['exhaust_pile']), 4)
        self.assertEqual(len(combat.player['discard_pile']), 1)

    def test_dark_embrace(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "dark_embrace": 1,
                    "carnage": 1,
                    "disarm": 1,
                    "power_through": 2
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        dark_embrace_id = get_key_by_substring(combat.player['hand'], 'dark_embrace')
        combat.take_action(f"play {dark_embrace_id}")
        self.assertEqual(len(combat.player['hand']), 4)
        self.assertEqual(len(combat.player['discard_pile']), 0)
        power_through_id = get_key_by_substring(combat.player['hand'], 'power_through')
        combat.take_action(f"play {power_through_id}")
        power_through_id_2 = get_key_by_substring(combat.player['hand'], 'power_through')
        combat.take_action(f"play {power_through_id_2}")
        self.assertEqual(len(combat.player['hand']), 6)

        enemy_id = combat.enemy_list[0]['id']
        disarm_id = get_key_by_substring(combat.player['hand'], 'disarm')
        combat.take_action(f"play {disarm_id} {enemy_id}")
        self.assertEqual(len(combat.player['hand']), 6)
        combat.take_action("end_turn")
        self.assertEqual(len(combat.player['hand']), 6)

    def test_disarm(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "disarm": 5,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        enemy_id = combat.enemy_list[0]['id']
        disarm_id = get_key_by_substring(combat.player['hand'], 'disarm')
        combat.take_action(f"play {disarm_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['strength'], -2)
        self.assertEqual(len(combat.player['exhaust_pile']), 1)
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 97)
        self.assertEqual(combat.enemy_list[0]['optional_dict']['strength'], -2)

    def test_dropkick(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "dropkick": 2,
                    "shockwave": 3,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        enemy_id = combat.enemy_list[0]['id']
        drop_kick_id = get_key_by_substring(combat.player['hand'], 'dropkick')
        shockwave_id = get_key_by_substring(combat.player['hand'], 'shockwave')
        combat.take_action(f"play {shockwave_id}")
        combat.take_action(f"play {drop_kick_id} {enemy_id}")
        drop_kick_id_2 = get_key_by_substring(combat.player['hand'], 'dropkick')
        combat.take_action(f"play {drop_kick_id_2} {enemy_id}")
        combat.take_action(f"play {drop_kick_id} {enemy_id}")
        combat.take_action(f"play {drop_kick_id_2} {enemy_id}")
        combat.take_action(f"play {drop_kick_id} {enemy_id}")
        combat.take_action(f"play {drop_kick_id_2} {enemy_id}")
        combat.take_action(f"play {drop_kick_id} {enemy_id}")

        self.assertEqual(combat.enemy_list[0]['hp'], 51)
        self.assertEqual(len(combat.player['hand']), 3)
        self.assertEqual(combat.player['energy'], 1)

    def test_dual_wield(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "dual_wield": 2,
                    "strike": 1,
                    "dark_embrace": 1,
                    "defend": 1
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        dual_wield_id = get_key_by_substring(combat.player['hand'], 'dual_wield')
        strike_id = get_key_by_substring(combat.player['hand'], 'strike')
        dark_embrace_id = get_key_by_substring(combat.player['hand'], 'dark_embrace')
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        self.assertIn(f"play {dual_wield_id} {strike_id}", combat.get_new_options())
        self.assertIn(f"play {dual_wield_id} {dark_embrace_id}", combat.get_new_options())
        self.assertNotIn(f"play {dual_wield_id} {defend_id}", combat.get_new_options())
        combat.take_action(f"play {dual_wield_id} {strike_id}")
        dual_wield_id_2 = get_key_by_substring(combat.player['hand'], 'dual_wield')
        combat.take_action(f"play {dual_wield_id_2} {dark_embrace_id}")
        self.assertEqual(len(combat.player['hand']), 5)
        self.assertEqual(len(combat.player['discard_pile']), 2)
        self.assertEqual(sum(1 for hand in combat.player['hand'].values() if hand['name'] == 'strike'), 2)

    def test_entrench(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "entrench": 3,
                    "power_through": 2
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        entrench_id = get_key_by_substring(combat.player['hand'], 'entrench')
        combat.take_action(f"play {entrench_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 0)
        power_through_id = get_key_by_substring(combat.player['hand'], 'power_through')
        entrench_id = get_key_by_substring(combat.player['hand'], 'entrench')
        combat.take_action(f"play {power_through_id}")
        combat.take_action(f"play {entrench_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 30)
        entrench_id = get_key_by_substring(combat.player['hand'], 'entrench')
        combat.take_action(f"play {entrench_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 60)

    def test_evolve(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "evolve": 1,
                    "power_through": 4
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['sentry'])
        evolve_id = get_key_by_substring(combat.player['hand'], 'evolve')
        combat.take_action(f"play {evolve_id}")
        for i in range(4):
            power_through_id = get_key_by_substring(combat.player['hand'], 'power_through')
            combat.take_action(f"play {power_through_id}")
        self.assertEqual(['end_turn'], combat.get_new_options())
        combat.take_action("end_turn")
        self.assertEqual(len(combat.player['hand']), 10)
    def test_feel_no_pain(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "feel_no_pain": 3,
                    "carnage": 1,
                    "shockwave": 1,
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        feel_no_pain_id = get_key_by_substring(combat.player['hand'], 'feel_no_pain')
        combat.take_action(f"play {feel_no_pain_id}")
        self.assertNotIn('block', combat.player['optional_dict'])
        shockwave_id = get_key_by_substring(combat.player['hand'], 'shockwave')
        combat.take_action(f"play {shockwave_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 3)
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 100)

    def test_fire_breathing(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "fire_breathing": 3,
                    "power_through": 1,
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['blockman'])
        fire_breathing_id = get_key_by_substring(combat.player['hand'], 'fire_breathing')
        combat.take_action(f"play {fire_breathing_id}")
        power_through_id = get_key_by_substring(combat.player['hand'], 'power_through')
        combat.take_action(f"play {power_through_id}")
        combat.take_action("end_turn")
        self.assertEqual(combat.enemy_list[0]['hp'], 8)

    def test_flame_barrier(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "flame_barrier": 5,
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        flame_barrier_id = get_key_by_substring(combat.player['hand'], 'flame_barrier')
        combat.take_action(f"play {flame_barrier_id}")
        combat.take_action("end_turn")
        self.assertEqual(combat.enemy_list[0]['hp'], 96)
        self.assertEqual(game_state['player']['hp'], 100)
        flame_barrier_id = get_key_by_substring(combat.player['hand'], 'flame_barrier')
        combat.take_action(f"play {flame_barrier_id}")
        flame_barrier_id = get_key_by_substring(combat.player['hand'], 'flame_barrier')
        combat.take_action(f"play {flame_barrier_id}")
        combat.take_action("end_turn")
        self.assertEqual(combat.enemy_list[0]['hp'], 88)
        self.assertEqual(game_state['player']['hp'], 100)

    def test_ghostly_armor(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "ghostly_armor": 5,
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        ghostly_armor_id = get_key_by_substring(combat.player['hand'], 'ghostly_armor')
        combat.take_action(f"play {ghostly_armor_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 10)
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 100)
        self.assertEqual(len(combat.player['hand']), 1)

    def test_hemokinesis(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "hemokinesis": 4,
                    "defend": 1
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        hemokinesis_id = get_key_by_substring(combat.player['hand'], 'hemokinesis')
        enemy_id = combat.enemy_list[0]['id']
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id}")
        combat.take_action(f"play {hemokinesis_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 85)
        self.assertEqual(game_state['player']['hp'], 98)

    def test_inflame(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "inflame": 4,
                    "heavy_blade": 1
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        inflame_id = get_key_by_substring(combat.player['hand'], 'inflame')
        combat.take_action(f"play {inflame_id}")
        self.assertEqual(combat.player['optional_dict']['strength'], 2)
        heavy_blade_id = get_key_by_substring(combat.player['hand'], 'heavy_blade')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play {heavy_blade_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 80)

    def test_intimidate(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "intimidate": 5,
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse', 'louse'])
        intimidate_id = get_key_by_substring(combat.player['hand'], 'intimidate')
        combat.take_action(f"play {intimidate_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['weak'], 1)
        self.assertEqual(combat.enemy_list[1]['optional_dict']['weak'], 1)
        intimidate_id = get_key_by_substring(combat.player['hand'], 'intimidate')
        combat.take_action(f"play {intimidate_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['weak'], 2)
        self.assertEqual(combat.enemy_list[1]['optional_dict']['weak'], 2)
        self.assertEqual(len(combat.player['exhaust_pile']), 2)

    def test_power_through(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "power_through": 4,
                    "draw_two": 1,
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        power_through_id = get_key_by_substring(combat.player['hand'], 'power_through')
        combat.take_action(f"play {power_through_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 15)
        self.assertEqual(len(combat.player['hand']), 6)
        power_through_id = get_key_by_substring(combat.player['hand'], 'power_through')
        combat.take_action(f"play {power_through_id}")
        self.assertEqual(len(combat.player['hand']), 7)
        power_through_id = get_key_by_substring(combat.player['hand'], 'power_through')
        combat.take_action(f"play {power_through_id}")
        self.assertEqual(len(combat.player['hand']), 8)
        power_through_id = get_key_by_substring(combat.player['hand'], 'power_through')
        combat.take_action(f"play {power_through_id}")
        self.assertEqual(len(combat.player['hand']), 9)
        draw_two_id = get_key_by_substring(combat.player['hand'], 'draw_two')
        combat.take_action(f"play {draw_two_id}")
        self.assertEqual(len(combat.player['hand']), 10)
        power_through_id = get_key_by_substring(combat.player['hand'], 'power_through')
        combat.take_action(f"play {power_through_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 75)
        self.assertEqual(len(combat.player['hand']), 10)
        self.assertEqual(len(combat.player['discard_pile']), 3)
        combat.take_action("end_turn")

    # def test_metallisize(self):

    def test_pummel(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "pummel": 4,
                    "flex": 1
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        pummel_id = get_key_by_substring(combat.player['hand'], 'pummel')
        enemy_id = combat.enemy_list[0]['id']
        flex_id = get_key_by_substring(combat.player['hand'], 'flex')
        combat.take_action(f"play {flex_id}")
        combat.take_action(f"play {pummel_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 84)
        self.assertEqual(len(combat.player['exhaust_pile']), 1)

    def test_rage(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "rage": 3,
                    "strike": 1,
                    "defend": 1
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        rage_id = get_key_by_substring(combat.player['hand'], 'rage')
        combat.take_action(f"play {rage_id}")
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        strike_id = get_key_by_substring(combat.player['hand'], 'strike')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play {defend_id}")
        combat.take_action(f"play {strike_id} {enemy_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 8)
        combat.take_action("end_turn")
        combat.take_action(f"play {strike_id} {enemy_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 0)

    def test_rampage(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "rampage": 5
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        rampage_id = get_key_by_substring(combat.player['hand'], 'rampage')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play {rampage_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 92)
        combat.take_action("end_turn")
        combat.take_action(f"play {rampage_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 79)
        rampage_id = get_key_by_substring(combat.player['hand'], 'rampage')
        combat.take_action(f"play {rampage_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 71)

    def test_reckless_charge(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "reckless_charge": 5,
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        reckless_charge_id = get_key_by_substring(combat.player['hand'], 'reckless_charge')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play {reckless_charge_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 93)
        self.assertEqual(len(combat.player['draw_pile']), 1)

    def test_rupture(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "rupture": 3,
                    "hemokinesis": 2,
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        rupture_id = get_key_by_substring(combat.player['hand'], 'rupture')
        combat.take_action(f"play {rupture_id}")
        enemy_id = combat.enemy_list[0]['id']
        hemokinesis_id = get_key_by_substring(combat.player['hand'], 'hemokinesis')
        combat.take_action(f"play {hemokinesis_id} {enemy_id}")
        self.assertEqual(combat.player['optional_dict']['strength'], 1)
        hemokinesis_id = get_key_by_substring(combat.player['hand'], 'hemokinesis')
        combat.take_action(f"play {hemokinesis_id} {enemy_id}")
        self.assertEqual(combat.player['optional_dict']['strength'], 2)
        self.assertEqual(combat.enemy_list[0]['hp'], 67)

    def test_second_wind(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "second_wind": 2,
                    "defend": 1,
                    "strike": 1,
                    "feel_no_pain": 1
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        second_wind_id = get_key_by_substring(combat.player['hand'], 'second_wind')
        combat.take_action(f"play {second_wind_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 15)
        self.assertEqual(len(combat.player['hand']), 1)
        self.assertEqual(len(combat.player['exhaust_pile']), 3)

    def test_seeing_red(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "seeing_red": 5,
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        seeing_red_id = get_key_by_substring(combat.player['hand'], 'seeing_red')
        combat.take_action(f"play {seeing_red_id}")
        self.assertEqual(combat.player['energy'], 11)
        self.assertEqual(len(combat.player['hand']), 4)
        self.assertEqual(len(combat.player['exhaust_pile']), 1)

    def test_sever_soul(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "sever_soul": 2,
                    "strike": 1,
                    "defend": 1,
                    "feel_no_pain": 1
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        sever_soul_id = get_key_by_substring(combat.player['hand'], 'sever_soul')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play {sever_soul_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 84)
        self.assertEqual(len(combat.player['hand']), 2)
        self.assertEqual(len(combat.player['exhaust_pile']), 2)

    def test_shockwave(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "shockwave": 5,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse', 'louse', 'louse'])
        shockwave_id = get_key_by_substring(combat.player['hand'], 'shockwave')
        combat.take_action(f"play {shockwave_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['vulnerable'], 3)
        self.assertEqual(combat.enemy_list[0]['optional_dict']['weak'], 3)
        self.assertEqual(combat.enemy_list[1]['optional_dict']['vulnerable'], 3)
        self.assertEqual(combat.enemy_list[1]['optional_dict']['weak'], 3)
        self.assertEqual(combat.enemy_list[2]['optional_dict']['vulnerable'], 3)
        self.assertEqual(combat.enemy_list[2]['optional_dict']['weak'], 3)

    def test_uppercut(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "uppercut": 5,
                    "defend": 1,
                    "strike": 1,
                    "feel_no_pain": 1
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        uppercut_id = get_key_by_substring(combat.player['hand'], 'uppercut')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play {uppercut_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['vulnerable'], 1)
        self.assertEqual(combat.enemy_list[0]['optional_dict']['weak'], 1)
        self.assertEqual(len(combat.player['hand']), 4)
        self.assertEqual(len(combat.player['exhaust_pile']), 0)

    def test_whirlwind(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "whirlwind": 5,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse', 'louse', 'louse'])
        whirlwind_id = get_key_by_substring(combat.player['hand'], 'whirlwind')
        combat.take_action(f"play {whirlwind_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 85)
        self.assertEqual(combat.enemy_list[1]['hp'], 85)
        self.assertEqual(combat.enemy_list[2]['hp'], 85)
        self.assertEqual(combat.player['energy'], 0)

    def test_barricade(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "barricade": 1,
                    "defend": 4,

                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        barricade_id = get_key_by_substring(combat.player['hand'], 'barricade')
        combat.take_action(f"play {barricade_id}")
        for i in range(4):
            defend_id = get_key_by_substring(combat.player['hand'], 'defend')
            combat.take_action(f"play {defend_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 20)
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 100)
        self.assertEqual(combat.player['optional_dict']['block'], 15)
        combat.take_action("end_turn")
        self.assertEqual(combat.player['optional_dict']['block'], 10)

    def test_berserk(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "berserk": 2,
                    "defend": 3,
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        berserk_id = get_key_by_substring(combat.player['hand'], 'berserk')
        combat.take_action(f"play {berserk_id}")
        berserk_id = get_key_by_substring(combat.player['hand'], 'berserk')
        combat.take_action(f"play {berserk_id}")
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 93)
        self.assertEqual(combat.player['energy'], 12)
        self.assertEqual(combat.player['optional_dict']['vulnerable'], 3)

    def test_bludgeon(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "bludgeon": 2,
                    "defend": 3,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        bludgeon_id = get_key_by_substring(combat.player['hand'], 'bludgeon')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play {bludgeon_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 68)

    def test_brutality(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "brutality": 10,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        brutality_id = get_key_by_substring(combat.player['hand'], 'brutality')
        combat.take_action(f"play {brutality_id}")
        brutality_id = get_key_by_substring(combat.player['hand'], 'brutality')
        combat.take_action(f"play {brutality_id}")
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 93)
        self.assertEqual(len(combat.player['hand']), 7)

    def test_demon_form(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "demon_form": 1,
                    "defend": 3,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        demon_form_id = get_key_by_substring(combat.player['hand'], 'demon_form')
        combat.take_action(f"play {demon_form_id}")
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 95)
        self.assertEqual(combat.player['optional_dict']['strength'], 2)
        combat.take_action("end_turn")
        self.assertEqual(combat.player['optional_dict']['strength'], 4)

    def test_double_tap(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "double_tap": 2,
                    "strike": 2,
                    "cleave": 1,
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse', 'louse'])
        double_tap_id = get_key_by_substring(combat.player['hand'], 'double_tap')
        strike_id = get_key_by_substring(combat.player['hand'], 'strike')
        combat.take_action(f"play {double_tap_id}")
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play {strike_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 88)
        double_tap_id = get_key_by_substring(combat.player['hand'], 'double_tap')
        combat.take_action(f"play {double_tap_id}")
        cleave_id = get_key_by_substring(combat.player['hand'], 'cleave')
        combat.take_action(f"play {cleave_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 72)
        self.assertEqual(combat.enemy_list[1]['hp'], 84)

    def test_exhume(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "exhume": 2,
                    "shockwave": 3
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        exhume_id = get_key_by_substring(combat.player['hand'], 'exhume')
        shockwave_id = get_key_by_substring(combat.player['hand'], 'shockwave')
        combat.take_action(f"play {shockwave_id}")
        combat.take_action(f"play {exhume_id} {shockwave_id}")
        self.assertEqual(len(combat.player['hand']), 4)
        self.assertEqual(len(combat.player['exhaust_pile']), 1)

    def test_immolate(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "immolate": 5,
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse', 'louse'])
        immolate_id = get_key_by_substring(combat.player['hand'], 'immolate')
        combat.take_action(f"play {immolate_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 79)
        self.assertEqual(combat.enemy_list[1]['hp'], 79)
        self.assertEqual(len(combat.player['hand']), 4)
        self.assertEqual(len(combat.player['discard_pile']), 2)
        self.assertIn('burn', [card['name'] for card in combat.player['discard_pile'].values()])

    def test_impervious(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "impervious": 5,
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse', 'louse'])
        impervious_id = get_key_by_substring(combat.player['hand'], 'impervious')
        combat.take_action(f"play {impervious_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 30)
        self.assertEqual(len(combat.player['hand']), 4)
        self.assertEqual(len(combat.player['exhaust_pile']), 1)

    def test_juggernaut(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "juggernaut": 2,
                    "defend": 1,
                    "rage": 1,
                    "strike": 1
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        juggernaut_id = get_key_by_substring(combat.player['hand'], 'juggernaut')
        combat.take_action(f"play {juggernaut_id}")
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 95)
        rage_id = get_key_by_substring(combat.player['hand'], 'rage')
        combat.take_action(f"play {rage_id}")
        strike_id = get_key_by_substring(combat.player['hand'], 'strike')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play {strike_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 84)

    def test_limit_break(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "limit_break": 2,
                    "flex": 3
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        flex_id = get_key_by_substring(combat.player['hand'], 'flex')
        combat.take_action(f"play {flex_id}")
        self.assertEqual(combat.player['optional_dict']['strength'], 2)
        limit_break_id = get_key_by_substring(combat.player['hand'], 'limit_break')
        combat.take_action(f"play {limit_break_id}")
        self.assertEqual(combat.player['optional_dict']['strength'], 4)
        flex_id = get_key_by_substring(combat.player['hand'], 'flex')
        combat.take_action(f"play {flex_id}")
        self.assertEqual(combat.player['optional_dict']['strength'], 6)
        limit_break_id = get_key_by_substring(combat.player['hand'], 'limit_break')
        combat.take_action(f"play {limit_break_id}")
        self.assertEqual(combat.player['optional_dict']['strength'], 12)
        combat.take_action("end_turn")
        self.assertEqual(combat.player['optional_dict']['strength'], 8)

    def test_offering(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "offering": 15,
                },
                "hp": 100,
                "max_energy": 10,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        offering_id = get_key_by_substring(combat.player['hand'], 'offering')
        combat.take_action(f"play {offering_id}")
        self.assertEqual(game_state['player']['hp'], 94)
        self.assertEqual(combat.player['energy'], 12)
        self.assertEqual(len(combat.player['hand']), 7)
        self.assertEqual(len(combat.player['exhaust_pile']), 1)

    def test_bandage_up(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "bandage_up": 5,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        bandage_up_id = get_key_by_substring(combat.player['hand'], 'bandage_up')
        combat.take_action(f"play {bandage_up_id}")
        self.assertEqual(game_state['player']['hp'], 100)
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 95)
        bandage_up_id = get_key_by_substring(combat.player['hand'], 'bandage_up')
        combat.take_action(f"play {bandage_up_id}")
        self.assertEqual(game_state['player']['hp'], 99)
        bandage_up_id = get_key_by_substring(combat.player['hand'], 'bandage_up')
        combat.take_action(f"play {bandage_up_id}")
        self.assertEqual(game_state['player']['hp'], 100)
        self.assertEqual(len(combat.player['hand']), 2)

    def test_blind(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "blind": 5
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        blind_id = get_key_by_substring(combat.player['hand'], 'blind')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play {blind_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['weak'], 2)
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 97)

    def test_dark_shackles(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "dark_shackles": 5
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        dark_shackles_id = get_key_by_substring(combat.player['hand'], 'dark_shackles')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play {dark_shackles_id} {enemy_id}")
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 100)
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 95)

    def test_finesse(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "finesse": 5,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        finesse_id = get_key_by_substring(combat.player['hand'], 'finesse')
        combat.take_action(f"play {finesse_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 2)
        self.assertEqual(len(combat.player['hand']), 4)
        self.assertEqual(len(combat.player['discard_pile']), 1)

    def test_flash_of_steel(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "flash_of_steel": 5,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        flash_of_steel_id = get_key_by_substring(combat.player['hand'], 'flash_of_steel')
        combat.take_action(f"play {flash_of_steel_id}")
        self.assertEqual(len(combat.player['hand']), 4)
        self.assertEqual(len(combat.player['discard_pile']), 1)
        flash_of_steel_id = get_key_by_substring(combat.player['hand'], 'flash_of_steel')
        combat.take_action(f"play {flash_of_steel_id}")
        self.assertEqual(len(combat.player['hand']), 4)
        self.assertEqual(len(combat.player['discard_pile']), 1)

    def test_good_instincts(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "good_instincts": 5,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        good_instincts_id = get_key_by_substring(combat.player['hand'], 'good_instincts')
        combat.take_action(f"play {good_instincts_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 6)
        self.assertEqual(len(combat.player['hand']), 4)
        self.assertEqual(len(combat.player['discard_pile']), 1)

    def test_panacea(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "panacea": 5,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['acid_slime_s'])
        panacea_id = get_key_by_substring(combat.player['hand'], 'panacea')
        combat.take_action(f"play {panacea_id}")
        self.assertNotIn('weak', combat.player['optional_dict'])
        combat.take_action("end_turn")
        self.assertNotIn('weak', combat.player['optional_dict'])

    def test_panic_button(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "panic_button": 1,
                    "defend": 4
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id}")
        panic_button_id = get_key_by_substring(combat.player['hand'], 'panic_button')
        combat.take_action(f"play {panic_button_id}")
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 35)
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 100)
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 0)
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 95)
        combat.take_action("end_turn")
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 5)

    def test_swift_strike(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "swift_strike": 5,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        swift_strike_id = get_key_by_substring(combat.player['hand'], 'swift_strike')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play {swift_strike_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 93)
        self.assertEqual(combat.player['energy'], 3)

    def test_trip(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {
                    "trip": 5,
                },
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {}
            }
        }

        combat = Combat(game_state, ['louse'])
        trip_id = get_key_by_substring(combat.player['hand'], 'trip')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play {trip_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['vulnerable'], 2)

    def test_panache(self):
        game_state = {
                    "floor_num": 1,
                    "act": 1,
                    "player": {
                        "deck": {
                            "panache": 1,
                            "draw_two": 4
                        },
                        "hp": 100,
                        "max_energy": 3,
                        "max_hp": 100,
                        "potions": {}
                    }
                }

        combat = Combat(game_state, ['louse', 'louse'])
        panache_id = get_key_by_substring(combat.player['hand'], 'panache')
        combat.take_action(f"play {panache_id}")
        for i in range(4):
            draw_two_id = get_key_by_substring(combat.player['hand'], 'draw_two')
            combat.take_action(f"play {draw_two_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 100)
        self.assertEqual(combat.enemy_list[1]['hp'], 100)
        draw_two_id = get_key_by_substring(combat.player['hand'], 'draw_two')
        combat.take_action(f"play {draw_two_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 90)
        self.assertEqual(combat.enemy_list[1]['hp'], 90)

    def test_block_potion(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {},
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {
                    "block_potion": 1
                }
            }
        }

        combat = Combat(game_state, ['louse'])
        block_potion_id = get_key_by_substring(combat.player['potions'], 'block_potion')
        combat.take_action(f"play_potion {block_potion_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 12)
        self.assertEqual(sum(combat.player['potions'].values()), 0)

    def test_dexterity_potion(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {"defend": 5},
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {
                    "dexterity_potion": 1
                }
            }
        }

        combat = Combat(game_state, ['louse'])
        dexterity_potion_id = get_key_by_substring(combat.player['potions'], 'dexterity_potion')
        combat.take_action(f"play_potion {dexterity_potion_id}")
        self.assertEqual(combat.player['optional_dict']['dexterity'], 2)
        self.assertEqual(sum(combat.player['potions'].values()), 0)
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 7)

    def test_energy_potion(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {"defend": 5},
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {
                    "energy_potion": 1
                }
            }
        }

        combat = Combat(game_state, ['louse'])
        energy_potion_id = get_key_by_substring(combat.player['potions'], 'energy_potion')
        combat.take_action(f"play_potion {energy_potion_id}")
        self.assertEqual(combat.player['energy'], 5)
        self.assertEqual(sum(combat.player['potions'].values()), 0)

    def test_explosive_potion(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {"defend": 5},
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {
                    "explosive_potion": 1
                }
            }
        }

        combat = Combat(game_state, ['louse', 'louse'])
        explosive_potion_id = get_key_by_substring(combat.player['potions'], 'explosive_potion')
        combat.take_action(f"play_potion {explosive_potion_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 90)
        self.assertEqual(combat.enemy_list[1]['hp'], 90)

    def test_fire_potion(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {"defend": 5},
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {
                    "fire_potion": 1
                }
            }
        }

        combat = Combat(game_state, ['louse'])
        fire_potion_id = get_key_by_substring(combat.player['potions'], 'fire_potion')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play_potion {fire_potion_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 80)

    def test_fruit_juice(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {"defend": 5},
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {
                    "fruit_juice": 1
                }
            }
        }

        combat = Combat(game_state, ['louse'])
        fruit_juice_id = get_key_by_substring(combat.player['potions'], 'fruit_juice')
        combat.take_action(f"play_potion {fruit_juice_id}")
        self.assertEqual(game_state['player']['hp'], 105)
        self.assertEqual(game_state['player']['max_hp'], 105)

    def test_fear_potion(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {"strike": 5},
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {
                    "fear_potion": 1
                }
            }
        }

        combat = Combat(game_state, ['louse'])
        fear_potion_id = get_key_by_substring(combat.player['potions'], 'fear_potion')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play_potion {fear_potion_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['vulnerable'], 3)
        strike_id = get_key_by_substring(combat.player['hand'], 'strike')
        combat.take_action(f"play {strike_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 91)
        self.assertEqual(sum(combat.player['potions'].values()), 0)

    def test_strength_potion(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {"strike": 5},
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {
                    "strength_potion": 1
                }
            }
        }

        combat = Combat(game_state, ['louse'])
        strength_potion_id = get_key_by_substring(combat.player['potions'], 'strength_potion')
        combat.take_action(f"play_potion {strength_potion_id}")
        self.assertEqual(combat.player['optional_dict']['strength'], 2)
        strike_id = get_key_by_substring(combat.player['hand'], 'strike')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play {strike_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['hp'], 92)
        self.assertEqual(sum(combat.player['potions'].values()), 0)

    def test_weak_potion(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {"strike": 5},
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {
                    "weak_potion": 1
                }
            }
        }

        combat = Combat(game_state, ['louse'])
        weak_potion_id = get_key_by_substring(combat.player['potions'], 'weak_potion')
        enemy_id = combat.enemy_list[0]['id']
        combat.take_action(f"play_potion {weak_potion_id} {enemy_id}")
        self.assertEqual(combat.enemy_list[0]['optional_dict']['weak'], 3)
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 97)
        self.assertEqual(sum(combat.player['potions'].values()), 0)

    def test_speed_potion(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {"defend": 5},
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {
                    "speed_potion": 1
                }
            }
        }

        combat = Combat(game_state, ['louse'])
        speed_potion_id = get_key_by_substring(combat.player['potions'], 'speed_potion')
        combat.take_action(f"play_potion {speed_potion_id}")
        self.assertEqual(sum(combat.player['potions'].values()), 0)
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 10)
        combat.take_action("end_turn")
        defend_id = get_key_by_substring(combat.player['hand'], 'defend')
        combat.take_action(f"play {defend_id}")
        self.assertEqual(combat.player['optional_dict']['block'], 5)

    def test_regen_potion(self):
        game_state = {
            "floor_num": 1,
            "act": 1,
            "player": {
                "deck": {"defend": 5},
                "hp": 100,
                "max_energy": 3,
                "max_hp": 100,
                "potions": {
                    "regen_potion": 1
                }
            }
        }

        combat = Combat(game_state, ['louse'])
        regen_potion_id = get_key_by_substring(combat.player['potions'], 'regen_potion')
        combat.take_action(f"play_potion {regen_potion_id}")
        self.assertEqual(sum(combat.player['potions'].values()), 0)
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 100)
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 99)
        combat.take_action("end_turn")
        self.assertEqual(game_state['player']['hp'], 97)

