import logging
import random
from fake_the_spire import FloorOver
from fake_the_spire.floor import Floor
from fake_the_spire.references import (EnemyReference, CardReference, CombatReference,
                                       generate_probability_list_from_probability_dict)

logger = logging.getLogger('flask_app')


class Combat(Floor):
    def __init__(self, game_state: dict, enemy_ids: list[str] = None, combat_type: str = "hallway"):
        super().__init__(game_state)
        self.floor_type = "combat"
        self.player = {'max_energy': game_state['player']['max_energy'], 'optional_dict': {}, 'hand': {}, 'energy': 0,
                       'draw_pile': self.generate_draw_pile(game_state['player']['deck']), 'discard_pile': {},
                       'potions': game_state['player']['potions']}
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
        return card_reference.generate_deck_dict_from_init_dict(init_deck)

    def to_dict(self):
        return {'player': self.player, 'enemy_list': self.enemy_list}

    def start_combat(self):
        self.get_new_enemy_action(is_first_turn=True)
        self.start_turn()

    def take_action(self, action: str):
        logger.debug(f'Action: {action}')
        logger.debug(f'Old state: {self.to_dict()}')
        action = action.split(' ')
        if action[0] == 'attack':
            self.attack(action[1:])
        elif action[0] == 'apply':
            self.apply(action[1:])
        elif action[0] == 'draw':
            self.draw()
        elif action[0] == 'play':
            self.play(action[1:])
        elif action[0] == 'end':
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
        else:
            logger.info(f'Invalid action: {action}')

        logger.debug(f'Updated state: {self.to_dict()}')
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

        if 'strength' in attacker['optional_dict']:
            attack_value += attacker['optional_dict']['strength']
        if 'weak' in attacker['optional_dict']:
            attack_value *= 0.75
        if 'vulnerable' in target['optional_dict']:
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

        if option_key in target['optional_dict']:
            target['optional_dict'][option_key] += option_value
        else:
            target['optional_dict'][option_key] = option_value

    def draw(self):
        if len(self.player['draw_pile']) == 0:
            self.player['draw_pile'] = self.player['discard_pile']
            self.player['discard_pile'] = {}
        if len(self.player['draw_pile']) > 0:
            random_card_id = random.choice(list(self.player['draw_pile'].keys()))
            random_card = self.player['draw_pile'].pop(random_card_id)
            self.player['hand'][random_card_id] = random_card

    def play(self, action: list[str]):
        card_id = action[0]
        card_actions = self.player['hand'][card_id]['actions']
        card_target = self.player['hand'][card_id]['target']
        if len(action) == 2:
            target_list = [self.get_enemy_by_id(action[1])]
        else:
            target_list = self.enemy_list
        for card_action in card_actions:
            if card_target == 'self':
                self.take_action(f"{card_action} player player")
            else:
                for target in target_list:
                    self.take_action(f"{card_action} player {target['id']}")

        if self.player['hand'][card_id]['type'] == 'skill':
            for enemy in self.enemy_list:
                if 'enrage' in enemy['optional_dict']:
                    self.take_action(f"apply strength {enemy['optional_dict']['enrage']} {enemy['id']} {enemy['id']}")
        if self.player['hand'][card_id]['type'] == 'attack':
            for enemy in self.enemy_list:
                if 'sharp_hide' in enemy['optional_dict']:
                    self.take_action(f"blockable_damage {enemy['optional_dict']['sharp_hide']} {enemy['id']} player")

        self.take_action(f'gain_energy -{self.player["hand"][card_id]["energy_cost"]}')
        self.player['discard_pile'][card_id] = self.player['hand'][card_id]
        self.player['hand'].pop(card_id)

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
        option_user = action[1]
        damage_target = action[2]
        self.damage_character(damage_target, damage_value)

    def add(self, action: list[str]):
        add_location = action[0]
        add_card = action[1]
        if add_location == 'discard':
            self.player['discard_pile'][add_card] = action[2]

    def damage_character(self, damage_target: str, damage_value: int):
        if damage_target == 'player':
            self.game_state['player']['hp'] -= damage_value
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


    def get_enemy_by_id(self, enemy_id: str) -> dict:
        for enemy in self.enemy_list:
            if enemy['id'] == enemy_id:
                return enemy
        raise KeyError(f'Enemy with id {enemy_id} not found')

    def get_new_options(self) -> (list[str], int):
        cards_in_hand = self.player['hand']
        enemies = self.enemy_list
        options = []
        for card_id, card in cards_in_hand.items():
            if card['energy_cost'] <= self.player['energy']:
                if card['target'] == 'enemy':
                    for enemy in enemies:
                        if enemy['hp'] >= 0:
                            enemy_id = enemy['id']
                            options.append(f'play {card_id} {enemy_id}')
                else:
                    options.append(f'play {card_id}')
        options.append('end')
        return options, 1

    def resolve_end_turn(self):
        self.player['energy'] = 0
        self.player['discard_pile'].update(self.player['hand'])
        self.player['hand'] = {}
        self.end_of_turn_optional_dict_update()
        for enemy in self.enemy_list:
            if enemy['hp'] > 0:
                self.resolve_enemy_action(enemy)
        self.start_turn()

    def resolve_enemy_action(self, enemy):
        enemy_action = enemy['intent']
        intent_action_list = enemy['actions'][enemy_action]
        for intent_action, intent_target in intent_action_list:
            self.take_action(f"{intent_action} {enemy['id']} {'player' if intent_target == 'player' else enemy['id']}")
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

                        valid_actions = {k: v for k,v in current_stage_dict['action_probabilities'].copy().items()
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
            for decrement_optional_key in ['vulnerable', 'weak']:
                if decrement_optional_key in character['optional_dict']:
                    character['optional_dict'][decrement_optional_key] = (
                            character['optional_dict'][decrement_optional_key] - 1)
                    if character['optional_dict'][decrement_optional_key] < 0:
                        character['optional_dict'][decrement_optional_key] = 0

    def start_turn(self):
        for i in range(5):
            self.take_action("draw")
        self.take_action(f'gain_energy {self.player["max_energy"]}')
