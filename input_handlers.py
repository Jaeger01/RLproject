import tcod as libtcod
from game_states import GameStates


def handle_keys(key, game_state):
    if game_state == GameStates.PLAYERS_TURN:
        return handle_player_turn(key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead(key)

    return {}


def handle_player_turn(key):
    key_char = chr(key.c)  # Gets key pressed

    # Movement keys for players
    if key.vk == libtcod.KEY_UP or key_char == 'w':
        return {'move': (0, -1)}
    elif key.vk == libtcod.KEY_DOWN or key_char == 'x':
        return {'move': (0, 1)}
    elif key.vk == libtcod.KEY_LEFT or key_char == 'a':
        return {'move': (-1, 0)}
    elif key.vk == libtcod.KEY_RIGHT or key_char == 'd':
        return {'move': (1, 0)}

    # The keys for diagonal movements
    elif key_char == 'q':
        return {'move': (-1, -1)}
    elif key_char == 'e':
        return {'move': (1, -1)}
    elif key_char == 'z':
        return {'move': (-1, 1)}
    elif key_char == 'c':
        return {'move': (1, 1)}

    if key_char == 'g':
        return {'pickup': True}

    if key_char == 'i':
        return {'show_inventory': True}

    if key_char == 'd':
        return {'drop_inventory': True}

    if key.vk == libtcod.KEY_ESCAPE:
        # Exit
        return{'exit': True}

    # Happens when no key is pressed
    return {}


def handle_targeting_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)

    if mouse.lbutton_pressed:
        return {'left_click': (x, y)}
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
