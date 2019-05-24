import tcod as libtcod
from input_handlers import *
from entity import *
from render_functions import *
from map_objects.map import Map

def main():
    #Globals
    screen_width = 100
    screen_height = 90
    map_width = 95
    map_height = 85

    room_max_size = 20
    room_min_size = 6
    max_rooms = 30

    colors = {
        'dark_wall': libtcod.Color(0,0, 100),
        'dark_ground': libtcod.Color(50,50, 100)
    }

    player = Entity(int(screen_width/2), int(screen_height/2), '@', libtcod.red)

    entities = [player]


    #Sets font and initializes screen information
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(screen_width, screen_height, 'RL Project', False)

    #Initializes new console
    main_console = libtcod.console_new(screen_width, screen_height)

    #Initializes map
    game_map = Map(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    #Game Loop
    while not libtcod.console_is_window_closed():
        #Captures events
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        #Draws all entities
        render_all(main_console, entities, game_map, screen_width, screen_height, colors)

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

        #exits if exit
        if exit:
            return True


if __name__ == '__main__':
    main()



