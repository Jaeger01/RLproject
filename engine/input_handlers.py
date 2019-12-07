import tcod as libtcod

from engine.game_states import GameStates


def handle_keys(key, game_state):
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn(key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead(key)
    elif game_state == GameStates.LOOK:
        return handle_look_menu(key)

    return {}


def handle_mouse(mouse, game_state):
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_mouse(mouse)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_mouse(mouse)

    return {}


def handle_player_turn(key):
    key_char = chr(key.c)  # Gets key pressed

    # Movement keys for players
    if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
        return {'move': (0, -1)}
    elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
        return {'move': (0, 1)}
    elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
        return {'move': (-1, 0)}
    elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
        return {'move': (1, 0)}

    # The keys for diagonal movements
    elif key.vk == libtcod.KEY_KP7:
        return {'move': (-1, -1)}
    elif key.vk == libtcod.KEY_KP9:
        return {'move': (1, -1)}
    elif key.vk == libtcod.KEY_KP1:
        return {'move': (-1, 1)}
    elif key.vk == libtcod.KEY_KP3:
        return {'move': (1, 1)}

    # keys to do things
    if key_char == 'l':
        return {'looking': True}

    if key_char == 'g':
        return {'pickup': True}

    if key_char == 'i':
        return {'show_inventory': True}

    if key_char == 'd':
        return {'drop_inventory': True}

    if key.vk == libtcod.KEY_KPADD:
        return {'take_stairs': True}

    if key.vk == libtcod.KEY_SPACE:
        return {'wait': True}

    if key_char == 'e':
        return {'interact': True}

    # Grimoire handling
    if key.vk == libtcod.KEY_1:
        return {'grimoire_index': 0}

    if key.vk == libtcod.KEY_2:
        return {'grimoire_index': 1}

    if key.vk == libtcod.KEY_3:
        return {'grimoire_index': 2}

    if key.vk == libtcod.KEY_4:
        return {'grimoire_index': 3}

    if key.vk == libtcod.KEY_5:
        return {'grimoire_index': 4}

    # Exit
    if key.vk == libtcod.KEY_ESCAPE:
        return{'exit': True}

    # Happens when no key is pressed
    return {}


def handle_player_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)

    if mouse.lbutton_pressed:
        return {'move': (x, y)}
    return {}


def handle_main_menu(key):
    key_char = chr(key.c)

    if key_char == 'a':
        return {'new_game': True}
    elif key_char == 'b':
        return {'load_game': True}
    elif key_char == 'c':
        return {'exit': True}

    return {}


def handle_look_menu(key):
    if key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}
    return {}


def handle_targeting_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)

    if mouse.lbutton_pressed:
        return {'target_click': (x, y)}
    elif mouse.rbutton_pressed:
        return {'right_click': (x, y)}
    return {}


def handle_targeting_keys(key):
    if key.vk == libtcod.KEY_ESCAPE:
        return {'exit': True}
    return {}


def handle_player_dead(key):
    key_char = chr(key.c)

    if key.vk == libtcod.KEY_ESCAPE:
        # Exit
        return{'exit': True}

    return {}


def handle_inventory(key):
    index = key.c - ord('a')

    if index >= 0:
        return {'inventory_index': index}

    if key.vk == libtcod.KEY_ESCAPE:
        # Exit
        return{'exit': True}

    return {}
