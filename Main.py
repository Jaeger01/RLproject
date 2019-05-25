import tcod as libtcod
from input_handlers import *
from entity import *
from render_functions import *
from map_objects.map import Map


def main():

    screen_width = 80
    screen_height = 80

    #Map variables
    map_width = 80
    map_height = 80
    room_max_size = 15
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10



    player = Entity(int(screen_width/2), int(screen_height/2), '@', libtcod.red)

    entities = [player]

    #Sets font and initializes screen information
    libtcod.console_set_custom_font('arial12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(screen_width, screen_height, 'RL Project', False, libtcod.RENDERER_SDL2)

    #Initializes new console
    main_console = libtcod.console_new(screen_width, screen_height)

    #Initializes map
    game_map = Map(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player)

    fov_recompute = True
    fov_map = initialize_fov(game_map)
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    #Game Loop
    while not libtcod.console_is_window_closed():
        FPS = libtcod.sys_get_fps()
        print(FPS)
        #Captures events
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        #Computes fov
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius)

        #Draws all entities
        render_all(main_console, entities, fov_map, fov_recompute, game_map, screen_width, screen_height, colors)
        fov_recompute = False #Dont want to recompute unnecessarily

        libtcod.console_flush()

        clear_all(main_console, entities)

        action = handle_keys(key)

        move = action.get('move')
        exit = action.get('exit')

        #moves if action is move
        if move:
            moveX, moveY = move
            if not game_map.is_blocked(player.x + moveX, player.y + moveY):
                player.move(moveX, moveY)
                fov_recompute = True

        #exits if exit
        if exit:
            return True


if __name__ == '__main__':
    main()



