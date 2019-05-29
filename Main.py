#mport tcod as libtcod
from input_handlers import *
from entity import *
from render_functions import *
from map_objects.map import Map
from game_states import GameStates
from components.fighter import Fighter
from components.inventory import Inventory
from death_functions import *
from game_messages import *


def main():

    screen_width = 80
    screen_height = 80

    # UI variables
    bar_width = 20
    panel_height = 10
    panel_y = screen_height - panel_height
    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    # Map variables
    map_width = 80
    map_height = 70
    room_max_size = 15
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 3
    max_items_per_room = 2
    fov_radius = 10

    fighter_component = Fighter(hp=30, defense_value=3, attack_value=5)
    inventory_component = Inventory(26)
    player = Entity(0, 0, '@', libtcod.red, 'Player', blocks=True, render_order=RenderOrder.ACTOR,
                    fighter=fighter_component, inventory=inventory_component)
    entities = [player]

    # Sets font and initializes screen information
    libtcod.console_set_custom_font('arial12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(screen_width, screen_height, 'RL Project', False, libtcod.RENDERER_SDL2)

    # Initializes new consoles
    main_console = libtcod.console_new(screen_width, screen_height)
    panel = libtcod.console_new(screen_width, panel_height)

    # Initializes map
    game_map = Map(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities,
                      max_monsters_per_room, max_items_per_room)

    # Initializes other game variables
    game_state = GameStates.PLAYERS_TURN
    prev_game_state = game_state
    fov_recompute = True
    fov_map = initialize_fov(game_map)
    message_log = MessageLog(message_x, message_width, message_height)
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    # Game Loop
    while not libtcod.console_is_window_closed():
        FPS = libtcod.sys_get_fps()
        libtcod.console_print_ex(main_console, 0, 0, libtcod.BKGND_NONE, libtcod.LEFT, 'FPS: {0}'.format(FPS))
        # Captures events
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        # Computes fov
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius)

        # Draws all entities, maps, and UI
        render_all(main_console, panel, entities, player, fov_map, fov_recompute, message_log, game_map, screen_width,
                   screen_height, bar_width, panel_height, panel_y, colors, game_state)

        fov_recompute = False  # Don't want to recompute unnecessarily

        libtcod.console_flush()

        clear_all(main_console, entities)

        # Action handling
        action = handle_keys(key, game_state)

        move = action.get('move')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        inventory_index = action.get('inventory_index')
        drop_inventory = action.get('drop_inventory')
        exit = action.get('exit')

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
                player_turn_results.extend(player.inventory.use(item))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        # Exits if exit
        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                game_state = prev_game_state
            else:
                return True

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')

            if message:
                message_log.add_message(message)

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
