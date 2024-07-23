import logging
import random
import itertools
import uuid

from fake_the_spire import FloorOver
from fake_the_spire.floor import Floor
from fake_the_spire.references import (EnemyReference, CardReference, CombatReference, PotionReference,
                                       generate_probability_list_from_probability_dict)

logger = logging.getLogger('flask_app')


class Combat(Floor):
    def __init__(self, game_state: dict, enemy_ids: list[str] = None, combat_type: str = "hallway"):
        super().__init__(game_state)
        self.floor_type = "combat"
        self.player = {'max_energy': game_state['player']['max_energy'], 'optional_dict': {}, 'hand': {}, 'energy': 0,
                       'draw_pile': self.generate_draw_pile(game_state['player']['deck']), 'discard_pile': {},
                       'potions': self.generate_potions(game_state['player']['potions']), 'top_of_deck_ids': [],
                       'exhaust_pile': {}}
        self.enemy_list = self.generate_enemies(game_state['act'], combat_type, enemy_ids)
        self.combat_type = combat_type
        self.start_combat()

    @staticmethod
    def generate_enemies(act: int, combat_type: str, enemy_ids: list[str] = None) -> list[dict]:
        enemy_reference = EnemyReference.get_instance()
        combat_reference = CombatReference.get_instance()
        if enemy_ids:
            return enemy_reference.generate_enemies_by_id_list(enemy_ids)
        enemy_ids = combat_reference.generate_enemies_by_combat_type_and_act(act, combat_type)
        return enemy_reference.generate_enemies_by_id_list(enemy_ids)

    @staticmethod
    def generate_draw_pile(init_deck: dict) -> dict:
        card_reference = CardReference.get_instance()
        return card_reference.generate_entity_dict_from_init_dict(init_deck)

    @staticmethod
    def generate_potions(init_potions: list[str]) -> dict:
        potion_reference = PotionReference.get_instance()
        return potion_reference.generate_entity_dict_from_init_dict(init_potions)

    def to_dict(self):
        return {'player': self.player, 'enemy_list': self.enemy_list}

    def start_combat(self):
        self.get_new_enemy_action(is_first_turn=True)
        self.start_turn()

    def take_action(self, action: str):
        action = super().take_action(action)
        if action is not None:
            if action[0] == 'attack':
                self.attack(action[1:])
            elif action[0] == 'apply':
                self.apply(action[1:])
            elif action[0] == 'draw':
                self.draw(action[1:])
            elif action[0] == 'play':
                self.play(action[1:])
            elif action[0] == 'play_potion':
                self.play_potion(action[1:])
            elif action[0] == 'end_turn':
                self.resolve_end_turn()
            elif action[0] == 'gain_energy':
                self.gain_energy(action[1:])
            elif action[0] == 'stage':
                self.update_stage(action[1:])
            elif action[0] == 'damage':
                self.damage(action[1:])
            elif action[0] == 'blockable_damage':
                self.blockable_damage(action[1:])
            elif action[0] == 'add':
                self.add_card(action[1:])
            elif action[0] == 'put':
                self.put_card(action[1:])
            elif action[0] == 'duplicate':
                self.duplicate_card(action[1:])
            elif action[0] == 'rampage':
                self.rampage(action[1:])
            else:
                logger.info(f'Invalid action: {action}')

        if all(enemy['hp'] <= 0 for enemy in self.enemy_list):
            raise FloorOver

    def attack(self, action: list[str]):
        attack_value = int(action[0])
        attacker_val = action[1]
        attack_target = action[2]

        if attack_target == 'player':
            target = self.player
        else:
            target = self.get_enemy_by_id(attack_target)
        if attacker_val == 'player':
            attacker = self.player
        else:
            attacker = self.get_enemy_by_id(attacker_val)

        if 'perfected_strike' in attacker['optional_dict']:
            strike_count = 0
            for card in attacker['hand'].values():
                if 'strike' in card['name']:
                    strike_count += 1
            for card in attacker['discard_pile'].values():
                if 'strike' in card['name']:
                    strike_count += 1
            for card in attacker['draw_pile'].values():
                if 'strike' in card['name']:
                    strike_count += 1
            attack_value += strike_count * attacker['optional_dict']['perfected_strike']

        if 'strength' in attacker['optional_dict']:
            if 'heavy_blade' in attacker['optional_dict']:
                for i in range(attacker['optional_dict']['heavy_blade'] - 1):
                    attack_value += attacker['optional_dict']['strength']
            attack_value += attacker['optional_dict']['strength']
        if 'body_slam' in attacker['optional_dict']:
            if 'block' in attacker['optional_dict']:
                attack_value += attacker['optional_dict']['block']
        if 'weak' in attacker['optional_dict']:
            if attacker['optional_dict']['weak'] > 0:
                attack_value *= 0.75
        if 'vulnerable' in target['optional_dict']:
            if target['optional_dict']['vulnerable'] > 0:
                if 'dropkick' in attacker['optional_dict']:
                    self.take_action("gain_energy 1")
                    self.take_action("draw")
                attack_value *= 1.5
        attack_value = int(attack_value)

        if 'block' in target['optional_dict']:
            original_attack_value = attack_value
            attack_value -= target['optional_dict']['block']
            if attack_value < 0:
                attack_value = 0
            target['optional_dict']['block'] -= original_attack_value
            if target['optional_dict']['block'] < 0:
                target['optional_dict']['block'] = 0
        if 'flame_barrier' in target['optional_dict']:
            self.damage_character(attacker_val, target['optional_dict']['flame_barrier'])
        if 'thorns' in target['optional_dict']:
            self.damage_character(attacker_val, target['optional_dict']['thorns'])
        self.damage_character(attack_target, attack_value)

    def apply(self, action: list[str]):
        option_key = action[0]
        option_value = int(action[1])
        option_user = action[2]
        option_target = action[3]
        if option_target == 'player':
            target = self.player
        else:
            target = self.get_enemy_by_id(option_target)

        if option_user == 'player':
            user = self.player
        else:
            user = self.get_enemy_by_id(option_user)

        if option_key == 'mode_shift':
            previous_mode_shift_count = int(user['optional_dict']['mode_shift_count'])
            option_value = option_value + (10 * previous_mode_shift_count)
            user['optional_dict']['mode_shift_count'] += 1

        if option_key == 'block':
            if 'entrench' in user['optional_dict'] and user['optional_dict']['entrench'] > 0:
                option_value += user['optional_dict']['block'] if 'block' in user['optional_dict'] else 0
            if 'second_wind' in user['optional_dict'] and user['optional_dict']['second_wind'] > 0:
                total_non_attack_cards = len([card for card in user['hand'].values() if card['type'] != 'attack']) - 1
                option_value += (user['optional_dict']['second_wind'] * total_non_attack_cards)
            if 'juggernaut' in user['optional_dict'] and user['optional_dict']['juggernaut'] > 0:
                random_enemy = random.choice(self.enemy_list)['id']
                self.take_action(f"blockable_damage {user['optional_dict']['juggernaut']} player {random_enemy}")
            if 'dexterity' in user['optional_dict']:
                option_value += user['optional_dict']['dexterity']

        if option_key == 'strength':
            if 'limit_break' in user['optional_dict'] and user['optional_dict']['limit_break'] > 0:
                option_value += user['optional_dict']['strength'] if 'strength' in user['optional_dict'] else 0

        if option_key in ['vulnerable', 'weak', 'frail']:
            if 'artifact' in target['optional_dict'] and target['optional_dict']['artifact'] > 0:
                target['optional_dict']['artifact'] -= 1
                return

        if option_key in target['optional_dict']:
            target['optional_dict'][option_key] += option_value
        else:
            target['optional_dict'][option_key] = option_value

    def draw(self, action: list[str]):
        if len(action) > 0:
            played_card_id = action[1]
        else:
            played_card_id = ''
        if 'battle_trance' in self.player['optional_dict'] and self.player['optional_dict']['battle_trance'] > 0:
            return
        if len(self.player['draw_pile']) == 0:
            self.player['draw_pile'] = self.player['discard_pile']
            self.player['discard_pile'] = {}
        if len(self.player['draw_pile']) > 0:
            if len(self.player['top_of_deck_ids']) > 0:
                card_id = self.player['top_of_deck_ids'].pop()
            else:
                card_id = random.choice(list(self.player['draw_pile'].keys()))
            if len([key for key in self.player['hand'].keys() if key != played_card_id]) < 10:
                card = self.player['draw_pile'].pop(card_id)
                self.player['hand'][card_id] = card
                if 'evolve' in self.player['optional_dict']:
                    if card['type'] == 'status':
                        self.take_action(f"draw")
                if 'fire_breathing' in self.player['optional_dict']:
                    if card['type'] in ['status', 'curse']:
                        for enemy in self.enemy_list:
                            self.take_action(f"blockable_damage {self.player['optional_dict']['fire_breathing']} "
                                             f"player {enemy['id']}")

    def play(self, action: list[str]):
        card_id = action[0]
        target_list = action[1:]
        card = self.player['hand'][card_id]

        if 'panache' in self.player['optional_dict'] and self.player['optional_dict']['panache'] > 0:
            if 'panache_count' not in self.player['optional_dict']:
                self.player['optional_dict']['panache_count'] = 0
            self.player['optional_dict']['panache_count'] += 1
            if self.player['optional_dict']['panache_count'] >= 5:
                self.player['optional_dict']['panache_count'] = 0
                for enemy in self.enemy_list:
                    self.take_action(f"blockable_damage {self.player['optional_dict']['panache']} player {enemy['id']}")

        # if 'duplication' in self.player['optional_dict'] and self.player['optional_dict']['duplication'] > 0:
        #     self.player['optional_dict']['duplication'] -= 1
        #     self.take_action(f"play {' '.join(action)}")

        if 'repeat' in card and card['repeat']:
            repeat_count = self.player['energy']
            energy_cost = 1
        else:
            repeat_count = 1
            energy_cost = card["energy_cost"]
        for i in range(repeat_count):
            if card_id not in self.player['hand']:
                print("BAD")
                print()
                print(self.player['hand'])
                print(card_id)
            self.resolve_action_list(card_id, "actions", target_list)
            self.take_action(f'gain_energy -{energy_cost}')

        if card['type'] == 'skill':
            for enemy in self.enemy_list:
                if 'enrage' in enemy['optional_dict']:
                    self.take_action(f"apply strength {enemy['optional_dict']['enrage']} {enemy['id']} {enemy['id']}")
        if card['type'] == 'attack':
            if 'double_tap' in self.player['optional_dict'] and self.player['optional_dict']['double_tap'] > 0:
                self.take_action(f"apply double_tap -1 player player")
                self.play(action)
            for enemy in self.enemy_list:
                if 'sharp_hide' in enemy['optional_dict']:
                    self.take_action(f"blockable_damage {enemy['optional_dict']['sharp_hide']} {enemy['id']} player")

            if 'rage' in self.player['optional_dict'] and self.player['optional_dict']['rage'] > 0:
                self.take_action(f"apply block {self.player['optional_dict']['rage']} player player")

        if card_id in self.player['hand']:
            if card['type'] != 'power':
                self.player['discard_pile'][card_id] = self.player['hand'][card_id]
            self.player['hand'].pop(card_id)

    def play_potion(self, action: list[str]):
        potion_id = action[0]
        target_list = action[1:]
        self.resolve_action_list(potion_id, "actions", target_list)

        if potion_id in self.player['potions']:
            self.player['potions'].pop(potion_id)

    def rampage(self, action: list[str]):
        rampage_value = int(action[0])
        rampage_card = action[2]
        enemy_id = action[3]

        attack_boost = self.player['optional_dict'][rampage_card] if rampage_card in self.player['optional_dict'] else 0
        self.take_action(f"attack {attack_boost + 8} player {enemy_id}")
        self.take_action(f"apply {rampage_card} {rampage_value} player player")

    def resolve_action_list(self, entity_id: str, action_keyword: str, target_list: list[str]):
        enemy_target_list = None
        discard_target_list = []
        hand_target_list = None
        for target in target_list:
            if self.get_enemy_by_id(target):
                enemy_target_list = [target]
            if target in self.player['discard_pile']:
                discard_target_list.append(target)
            if target in self.player['hand']:
                hand_target_list = [target]
        if enemy_target_list is None:
            enemy_target_list = [enemy['id'] for enemy in self.enemy_list]
        if hand_target_list is None:
            hand_target_list = [card_id for card_id, card_dict in self.player['hand'].items()]
        hand_target_non_attack_list = [_card_id for _card_id, card_dict in self.player['hand'].items()
                                       if card_dict['type'] != 'attack' and _card_id != entity_id]

        target_dict = {'hand': hand_target_list, 'discard_pile': discard_target_list,
                       'enemy': enemy_target_list, 'card': entity_id, 'hand_non_attack': hand_target_non_attack_list,
                       'exhaust': [card_id for card_id, card_dict in self.player['exhaust_pile'].items()]}

        if entity_id in self.player['hand']:
            card = self.player['hand'][entity_id]
            actions_targets = card[action_keyword]
            is_card = True
        else:
            potion = self.player['potions'][entity_id]
            actions_targets = potion[action_keyword]
            is_card = False
        for (action, target) in actions_targets:
            target_string_list = self.generate_target_string_list(target, target_dict)
            for target_string in target_string_list:
                card_action_list = action.split(' ')
                if card_action_list[0] == 'apply' and card_action_list[1] == 'block':
                    if ('panic_button' in self.player['optional_dict'] and
                            self.player['optional_dict']['panic_button'] > 0 and is_card):
                        card_action_list[2] = '0'
                card_action = ' '.join(card_action_list)
                self.take_action(f"{card_action} player {target_string}")

    @staticmethod
    def generate_target_string_list(card_target: str, target_dict: dict) -> list[str]:
        enemy_target_list = target_dict['enemy']
        if card_target == 'self':
            return ['player']
        if card_target == 'random_enemy':
            return [f'{random.choice(enemy_target_list)}']
        if card_target == 'hand':
            return [' '.join(target_dict['hand'])]
        if card_target == 'discard_pile':
            return [' '.join(target_dict['discard_pile'])]
        if card_target == 'enemy':
            target_list = []
            for target in enemy_target_list:
                target_list.append(target)
            return target_list
        if card_target == 'self_card':
            return [target_dict['card']]
        if card_target == 'random_hand':
            target_dict["hand"].remove(target_dict["card"])
            return [f'{random.choice(target_dict["hand"])}']
        if card_target == 'self_card_enemy':
            target_list = []
            for target in enemy_target_list:
                target_list.append(f'{target_dict["card"]} {target}')
            return target_list
        if card_target in target_dict:
            return target_dict[card_target]
        raise KeyError(f"Missing {card_target} from generate_target_string_list function")

    def gain_energy(self, action: list[str]):
        amount = int(action[0])
        self.player['energy'] += amount

    def update_stage(self, action: list[str]):
        new_stage = action[0]
        enemy_stage_to_update = action[1]
        enemy = self.get_enemy_by_id(enemy_stage_to_update)
        enemy['stage'] = new_stage
        if enemy[new_stage]['action_choose_type'] == 'ordered':
            enemy['current_stage_action_key'] = 0

    def spawn_enemy(self, action: list[str]):
        new_enemy = action[0]
        enemy_reference = EnemyReference.get_instance()
        enemy = enemy_reference.generate_enemy_by_id(new_enemy)
        self.enemy_list.append(enemy)

    def blockable_damage(self, action: list[str]):
        damage_value = int(action[0])
        damage_user = action[1]
        damage_target = action[2]

        if damage_target == 'player':
            target = self.player
        else:
            target = self.get_enemy_by_id(damage_target)
        if damage_user == 'player':
            user = self.player
        else:
            user = self.get_enemy_by_id(damage_user)

        if 'block' in target['optional_dict']:
            original_attack_value = damage_value
            damage_value -= target['optional_dict']['block']
            if damage_value < 0:
                damage_value = 0
            target['optional_dict']['block'] -= original_attack_value
            if target['optional_dict']['block'] < 0:
                target['optional_dict']['block'] = 0

        self.damage_character(damage_target, damage_value)

    def damage(self, action: list[str]):
        damage_value = int(action[0])
        damager = action[1]
        damage_target = action[2]
        if damager == 'player' and damage_target == 'player':
            if 'rupture' in self.player['optional_dict'] and self.player['optional_dict']['rupture'] > 0:
                self.take_action(f"apply strength {self.player['optional_dict']['rupture']} player player")

        self.damage_character(damage_target, damage_value)

    def add_card(self, action: list[str]):
        add_location = action[0]
        add_card = action[1]
        card_id = action[3]
        card_reference = CardReference.get_instance()
        card = card_reference.generate_entity_by_name(add_card)
        if add_location == 'discard':
            self.player['discard_pile'].update(card)
        if add_location == 'draw':
            self.player['draw_pile'].update(card)
        if add_location == 'hand':
            if len([key for key in self.player['hand'] if key != card_id]) > 9:
                self.player['discard_pile'].update(card)
            else:
                self.player['hand'].update(card)

    def put_card(self, action: list[str]):
        card_ids = action[3:]
        if card_ids == ['']:
            return
        source = action[0]
        destination = action[1]
        temp_card_pile = {}
        for card_id in card_ids:
            if source == 'discard':
                temp_card_pile[card_id] = self.player['discard_pile'][card_id]
                del self.player['discard_pile'][card_id]
            if source == 'hand':
                temp_card_pile[card_id] = self.player['hand'][card_id]
                del self.player['hand'][card_id]
            if source == 'exhaust':
                temp_card_pile[card_id] = self.player['exhaust_pile'][card_id]
                del self.player['exhaust_pile'][card_id]
            if destination == 'draw_top':
                self.player['top_of_deck_ids'].append(card_id)
                self.player['draw_pile'][card_id] = temp_card_pile[card_id]
            if destination == 'exhaust':
                if 'dark_embrace' in self.player['optional_dict']:
                    for i in range(self.player['optional_dict']['dark_embrace']):
                        self.take_action("draw")
                if 'feel_no_pain' in self.player['optional_dict']:
                    self.take_action(f"apply block {self.player['optional_dict']['feel_no_pain']} player player")
                self.player['exhaust_pile'][card_id] = temp_card_pile[card_id]
            if destination == 'hand':
                self.player['hand'][card_id] = temp_card_pile[card_id]

    def duplicate_card(self, action: list[str]):
        card_id = action[1]
        card = self.player['hand'][card_id]
        self.player['hand'][f'{card["name"]}_{uuid.uuid4()}'] = card

    def damage_character(self, damage_target: str, damage_value: int):
        if damage_value <= 0:
            return
        if damage_target == 'player':
            self.game_state['player']['hp'] -= damage_value
            self.take_action("apply damage_instances 1 player player")
        else:
            enemy = self.get_enemy_by_id(damage_target)
            enemy['hp'] -= damage_value
            if 'mode_shift' in enemy['optional_dict']:
                enemy['optional_dict']['mode_shift'] -= damage_value
                if enemy['optional_dict']['mode_shift'] <= 0:
                    del enemy['optional_dict']['mode_shift']
                    enemy['stage'] = 'defensive_mode'
                    enemy['current_stage_action_key'] = 0
                    self.get_new_enemy_action()

    def get_enemy_by_id(self, enemy_id: str) -> dict | None:
        for enemy in self.enemy_list:
            if enemy['id'] == enemy_id:
                return enemy
        return None

    def get_new_options(self) -> list[str]:
        cards_in_hand = self.player['hand']
        potions = self.player['potions']
        options = []
        target_dict = {'enemy': self.generate_attackable_enemy_list(),
                       'discard_pile': self.generate_discard_pile_list(),
                       'hand': self.generate_hand_list(),
                       'attack_and_powers_in_hand': self.generate_filtered_hand_list('hand',
                                                                                     [('type',
                                                                                       ['power', 'attack'])])}
        for card_id, card in cards_in_hand.items():
            if self.is_card_is_playable(card):
                target_option_list = self.generate_target_option_list(card, target_dict)
                for target_id in target_option_list:
                    if card_id == target_id:
                        continue
                    options.append(f"play {card_id} {target_id}")
                if len(target_option_list) == 0:
                    options.append(f'play {card_id}')
        for potion_id, potion in potions.items():
            target_option_list = self.generate_target_option_list(potion, target_dict)
            for target_id in target_option_list:
                if potion_id == target_id:
                    continue
                options.append(f"play_potion {potion_id} {target_id}")
            if len(target_option_list) == 0:
                options.append(f'play_potion {potion_id}')

        options.append('end_turn')
        return options

    def generate_attackable_enemy_list(self) -> list[str]:
        enemy_list = []
        for enemy in self.enemy_list:
            if enemy['hp'] >= 0:
                enemy_list.append(enemy['id'])
        return enemy_list

    def generate_discard_pile_list(self) -> list[str]:
        discard_list = []
        for card in self.player['discard_pile'].items():
            discard_list.append(card[0])
        return discard_list

    def generate_hand_list(self) -> list[str]:
        hand_list = []
        for card in self.player['hand'].items():
            hand_list.append(card[0])
        return hand_list

    def generate_filtered_hand_list(self, search_location: str, search_list: list) -> list[str]:
        filtered_hand_list = []
        for card in self.player[search_location].items():
            if all(search_keyword in card[1] and card[1][search_keyword] in search_value
                   for (search_keyword, search_value) in search_list):
                filtered_hand_list.append(card[0])
        return filtered_hand_list

    @staticmethod
    def generate_target_option_list(card: dict, target_dict: dict) -> list[str]:
        selected_lists = []
        for keyword in card['target']:
            if keyword in target_dict:
                selected_lists.append(target_dict[keyword])
        combinations = list(itertools.product(*selected_lists))
        target_option_list = [' '.join(combination) for combination in combinations]
        return target_option_list

    def is_card_is_playable(self, card: dict) -> bool:
        if card['actions'] == 'unplayable':
            return False

        if card['name'] == 'clash':
            count_of_attacks_in_hand = len({k: v for k, v in self.player['hand'].items()
                                            if 'type' in v and v['type'] == 'attack'})
            if count_of_attacks_in_hand > 1:
                return False

        if card['name'] == 'blood_for_blood':
            if 'damage_instances' in self.player['optional_dict']:
                card['energy_cost'] -= self.player['optional_dict']['damage_instances']
        # if card['name'] == 'spot_weakness':
        #     all_enemy_actions = [enemy['actions'][enemy['intent']] for enemy in self.enemy_list]
        #     all_enemy_actions = list(itertools.chain.from_iterable(all_enemy_actions))
        if card['energy_cost'] > self.player['energy']:
            return False
        return True

    def resolve_end_turn(self):
        for enemy in self.enemy_list:
            if enemy['hp'] > 0:
                self.resolve_enemy_action(enemy, after_player_update=False)
        self.player['energy'] = 0
        self.end_of_turn_hand_update()
        self.end_of_turn_optional_dict_update()
        for enemy in self.enemy_list:
            if enemy['hp'] > 0:
                self.resolve_enemy_action(enemy, after_player_update=True)
        self.start_turn()

    def end_of_turn_hand_update(self):
        hand_copy = self.player['hand'].copy()
        for card_id, card in hand_copy.items():
            if 'end_of_turn' in card:
                self.resolve_action_list(card_id, 'end_of_turn', [])
            else:
                card = self.player['hand'].pop(card_id)
                self.player['discard_pile'][card_id] = card

    def resolve_enemy_action(self, enemy, after_player_update):
        enemy_action = enemy['intent']
        intent_action_list = enemy['actions'][enemy_action]
        keyword_list = ['apply']
        for intent_action, intent_target in intent_action_list:
            keyword = intent_action.split(' ')[0]
            if (after_player_update and keyword in keyword_list) or (
                    not after_player_update and keyword not in keyword_list):
                self.take_action(
                    f"{intent_action} {enemy['id']} {'player' if intent_target == 'player' else enemy['id']}")
        if after_player_update:
            enemy['action_history'].append(enemy_action)
            self.get_new_enemy_action()

    def get_new_enemy_action(self, is_first_turn: bool = False):
        for enemy in self.enemy_list:
            chose_first_intent = False
            if is_first_turn:
                if 'action_start_combat' in enemy:
                    enemy['intent'] = enemy['action_start_combat']
                    chose_first_intent = True
            if not chose_first_intent:
                current_stage_dict = enemy[enemy['stage']]
                if current_stage_dict['action_choose_type'] == 'random':
                    if len(enemy['action_history']) > 0:
                        previous_action = enemy['action_history'][-1]
                        previous_action_consecutive_amount = 0
                        for action in enemy['action_history'][::-1]:
                            if action == previous_action:
                                previous_action_consecutive_amount += 1
                            else:
                                break

                        valid_actions = {k: v for k, v in current_stage_dict['action_probabilities'].copy().items()
                                         if 'action_max_consecutive' not in current_stage_dict or
                                         k != previous_action or
                                         current_stage_dict['action_max_consecutive'][k] <
                                         previous_action_consecutive_amount}
                    else:
                        valid_actions = current_stage_dict['action_probabilities'].copy()

                    action_names, action_weights = generate_probability_list_from_probability_dict(
                        valid_actions)
                    random_action = random.choices(action_names, weights=action_weights)
                    enemy['intent'] = random_action[0]
                elif current_stage_dict['action_choose_type'] == 'ordered':
                    if 'current_stage_action_key' in enemy:
                        current_stage_action_key = enemy['current_stage_action_key']
                    else:
                        current_stage_action_key = 0
                    enemy['intent'] = current_stage_dict['action_order'][current_stage_action_key]
                    if current_stage_action_key == len(current_stage_dict['action_order']) - 1:
                        enemy['current_stage_action_key'] = 0
                    else:
                        enemy['current_stage_action_key'] = current_stage_action_key + 1

    def end_of_turn_optional_dict_update(self):
        alive_characters = [enemy for enemy in self.enemy_list if enemy['hp'] > 0] + [self.player]
        for character in alive_characters:
            for decrement_optional_key in ['vulnerable', 'weak', 'frail', 'panic_button']:
                if decrement_optional_key in character['optional_dict']:
                    character['optional_dict'][decrement_optional_key] = (
                            character['optional_dict'][decrement_optional_key] - 1)
                    if character['optional_dict'][decrement_optional_key] < 0:
                        character['optional_dict'][decrement_optional_key] = 0
            if 'strength_buff' in character['optional_dict']:
                if 'strength' not in character['optional_dict']:
                    character['optional_dict']['strength'] = 0
                character['optional_dict']['strength'] += character['optional_dict']['strength_buff']
                character['optional_dict']['strength_buff'] = 0
            if 'dexterity_buff' in character['optional_dict']:
                if 'dexterity' not in character['optional_dict']:
                    character['optional_dict']['dexterity'] = 0
                character['optional_dict']['dexterity'] += character['optional_dict']['dexterity_buff']
                character['optional_dict']['dexterity_buff'] = 0
            if 'battle_trance' in character['optional_dict']:
                character['optional_dict']['battle_trance'] = 0
            if 'flame_barrier' in character['optional_dict']:
                character['optional_dict']['flame_barrier'] = 0
            if 'rage' in character['optional_dict']:
                character['optional_dict']['rage'] = 0
            if 'block' in character['optional_dict']:
                if not ('barricade' in character['optional_dict'] and character['optional_dict']['barricade'] > 0):
                    character['optional_dict']['block'] = 0
            if 'ritual' in character['optional_dict']:
                if 'strength' in character['optional_dict']:
                    character['optional_dict']['strength'] += character['optional_dict']['ritual']
                else:
                    character['optional_dict']['strength'] = character['optional_dict']['ritual']
            if 'regen' in character['optional_dict'] and character['optional_dict']['regen'] > 0:
                self.take_action(f"heal {character['optional_dict']['regen']}")
                character['optional_dict']['regen'] -= 1

    def start_turn(self):
        for i in range(5):
            self.take_action("draw")
        if 'berserk' in self.player['optional_dict']:
            for i in range(self.player['optional_dict']['berserk']):
                self.take_action("gain_energy 1")
        if 'brutality' in self.player['optional_dict']:
            for i in range(self.player['optional_dict']['brutality']):
                self.take_action("draw")
                self.take_action("damage 1 player player")
        self.take_action(f'gain_energy {self.player["max_energy"]}')
