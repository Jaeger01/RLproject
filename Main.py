#mport tcod as libtcod
from input_handlers import *
from entity import *
from render_functions import *
from map_objects.map import Map
from game_states import GameStates
from components.fighter import Fighter
from death_functions import *


def main():

    screen_width = 80
    screen_height = 80

    # Map variables
    map_width = 80
    map_height = 80
    room_max_size = 15
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 3
    fov_radius = 10

    fighter_component = Fighter(hp=30, defense_value=3, attack_value=5)
    player = Entity(0, 0, '@', libtcod.red, 'Player', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component)
    entities = [player]

    # Sets font and initializes screen information
    libtcod.console_set_custom_font('arial12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(screen_width, screen_height, 'RL Project', False, libtcod.RENDERER_SDL2)

    # Initializes new console
    main_console = libtcod.console_new(screen_width, screen_height)

    # Initializes map
    game_map = Map(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room)

    # Initializes other game variables
    game_state = GameStates.PLAYERS_TURN
    fov_recompute = True
    fov_map = initialize_fov(game_map)
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    # Game Loop
    while not libtcod.console_is_window_closed():
        FPS = libtcod.sys_get_fps()
       # print(FPS)
        # Captures events
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        # Computes fov
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius)

        # Draws all entities
        render_all(main_console, entities, player, fov_map, fov_recompute, game_map, screen_width, screen_height, colors)
        fov_recompute = False  # Don't want to recompute unnecessarily

        libtcod.console_flush()

        clear_all(main_console, entities)

        action = handle_keys(key)

        move = action.get('move')
        exit = action.get('exit')

        # Does player turn
        player_turn_results = []
        if move and game_state == GameStates.PLAYERS_TURN:
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

        # Exits if exit
        if exit:
            return True

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('messages')
            dead_entity = player_turn_result.get('dead')

            if message:
                print(message)
            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                print(message)

        # Does enemy turn
        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('messages')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            print(message)
                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            print(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
    main()



