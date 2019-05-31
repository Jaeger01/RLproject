from input_handlers import *
from render_functions import *
from death_functions import *
from game_messages import *
from loader_functions.initialize_new_game import *
from loader_functions.data_loaders import *


def main():
    constant_variables = get_constant_variables()

    # Sets fonts root console
    libtcod.console_set_custom_font('arial12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(constant_variables['screen_width'], constant_variables['screen_height'],
                              constant_variables['window_title'], False, libtcod.RENDERER_SDL2)

    # Initializes consoles
    main_console = libtcod.console_new(constant_variables['screen_width'], constant_variables['screen_height'])
    panel = libtcod.console_new(constant_variables['screen_width'], constant_variables['panel_height'])

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = libtcod.image_load('menu_background.png')

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            main_menu(main_console, main_menu_background_image, constant_variables['screen_width'],
                      constant_variables['screen_height'])

            if show_load_error_message:
                message_box(main_console, 'No save game to load', 40, constant_variables['screen_width'],
                            constant_variables['screen_height'])

            libtcod.console_flush()

            action = handle_main_menu(key)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
            elif new_game:
                player, entities, game_map, game_state, message_log = get_game_variables(constant_variables)
                game_state = GameStates.PLAYERS_TURN

                show_main_menu = False
            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break

        else:
            libtcod.console_clear(main_console)
            play_game(player, entities, game_map, message_log, game_state, main_console, panel, constant_variables)

            show_main_menu = True


def play_game(player, entities, game_map, message_log, game_state, main_console, panel, constant_variables):
    # Initializes all main game variables
    prev_game_state = game_state
    fov_recompute = True
    fov_map = initialize_fov(game_map)
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    targeting_item = None

    # Game Loop
    while not libtcod.console_is_window_closed():
        fps = libtcod.sys_get_fps()
        libtcod.console_print_ex(main_console, 0, 0, libtcod.BKGND_NONE, libtcod.LEFT, 'FPS: {0}'.format(fps))
        # Captures events
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        # Computes fov
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constant_variables['fov_radius'])

        # Draws all entities, maps, and UI
        render_all(main_console, panel, entities, player, fov_map, fov_recompute, message_log, game_map,
                   constant_variables['screen_width'],
                   constant_variables['screen_height'], constant_variables['bar_width'],
                   constant_variables['panel_height'],
                   constant_variables['panel_y'], colors, game_state)

        fov_recompute = False  # Don't want to recompute unnecessarily

        libtcod.console_flush()

        clear_all(main_console, entities)

        # Action handling
        action = handle_keys(key, game_state)
        mouse_action = handle_targeting_mouse(mouse)

        move = action.get('move')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        inventory_index = action.get('inventory_index')
        drop_inventory = action.get('drop_inventory')
        exit = action.get('exit')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        # Does player turn
        player_turn_results = []
        if move and game_state == GameStates.PLAYERS_TURN:
            start = Message('----Start of Turn----')
            message_log.add_message(start)

            moveX, moveY = move
            destination_x = player.x + moveX
            destination_y = player.y + moveY

            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(moveX, moveY)
                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

        # Handles pickups
        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)

                    break
            else:
                message_log.add_message(Message('There is nothing to get', libtcod.yellow))

        if show_inventory:
            prev_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            prev_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if inventory_index is not None and prev_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]
            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                                                        target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        # Exits if exit
        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                game_state = prev_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                save_game(player, entities, game_map, message_log, game_state)
                return True

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')

            if message:
                message_log.add_message(message)

            if targeting_cancelled:
                game_state = prev_game_state

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            # Handles pickup/consume
            if item_added:
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if item_dropped:
                entities.append(item_dropped)
                game_state == GameStates.ENEMY_TURN

            if targeting:
                prev_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING
                targeting_item = targeting
                message_log.add_message(targeting_item.item.targeting_message)

        # Does enemy turn
        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
    main()
