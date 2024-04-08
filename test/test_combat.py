import unittest

from fake_the_spire import GameOver, FloorOver
from fake_the_spire.combat import Combat


class TestCombat(unittest.TestCase):
    def test_apply_block_play_defend(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "defend": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5
            }
        }
        combat = Combat(game_state)
        combat.take_action("play defend_0")
        self.assertEqual(combat.player['optional_dict']['block'], 5)

    def test_deal_damage_play_strike(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "strike": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5
            }
        }
        combat = Combat(game_state, ['louse'])
        combat.take_action(f"play strike_0 louse")
        self.assertEqual(combat.enemy_list[0]['hp'], 94)

    def test_add_vuln_deal_damage_play_bash(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "bash": 5
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5
            }
        }
        combat = Combat(game_state, ['louse'])
        combat.take_action(f"play bash_0 louse")
        self.assertEqual(combat.enemy_list[0]['hp'], 92)
        self.assertEqual(combat.enemy_list[0]['optional_dict']['vulnerable'], 2)

    def test_strike_vuln_target(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "bash": 3,
                    "strike": 2
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5
            }
        }
        combat = Combat(game_state, ['louse'])
        combat.take_action("play bash_0 louse")
        combat.take_action("play strike_0 louse")
        self.assertEqual(combat.enemy_list[0]['hp'], 83)
        self.assertEqual(combat.enemy_list[0]['optional_dict']['vulnerable'], 2)

    def test_draw_no_deck(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "draw_two": 5,
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5
            }
        }
        combat = Combat(game_state, ['louse'])
        combat.take_action("play draw_two_0")
        self.assertEqual(len(combat.player['hand']), 4)

    def test_end_turn_enemy_take_action(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "bash": 3,
                    "strike": 2
                },
                "hp": 10,
                "max_energy": 3,
                "max_hp": 10
            }
        }
        combat = Combat(game_state, ['louse'])
        combat.take_action("end")
        self.assertEqual(combat.player['hp'], 5)

    def test_game_over_combat_damage(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "bash": 3,
                    "strike": 2
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5
            }
        }
        combat = Combat(game_state, ['louse'])
        with self.assertRaises(GameOver):
            combat.take_action("end")
        self.assertLessEqual(combat.player['hp'], 0)

    def test_floor_over_won_combat(self):
        game_state = {
            "floor_num": 1,
            "player": {
                "deck": {
                    "bash": 3,
                    "strike": 2
                },
                "hp": 5,
                "max_energy": 3,
                "max_hp": 5
            }
        }
        combat = Combat(game_state, ['weakling'])
        with self.assertRaises(FloorOver):
            combat.take_action("play strike_0 weakling")
