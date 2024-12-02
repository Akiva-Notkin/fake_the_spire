import unittest
import logging

from fake_the_spire.combat import Combat

logging.basicConfig(level=logging.INFO)


def get_key_by_substring(dictionary, substring):
    for key in dictionary:
        if substring in key:
            return key
class TestCombat(unittest.TestCase):

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


