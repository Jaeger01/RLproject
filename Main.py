import tcod as libtcod
from input_handlers import *


def main():
    #Globals
    screen_width = 100
    screen_height = 90
    playerX = int(screen_width/2)
    playerY = int(screen_height/2)


    #Sets font and initializes screen information
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(screen_width, screen_height, 'RL Project', False)

    #Declares new console
    main_console = libtcod.console_new(screen_width, screen_height)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    #Game Loop
    while not libtcod.console_is_window_closed():
        #Captures events
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        libtcod.console_set_default_foreground(main_console, libtcod.white)
        libtcod.console_put_char(main_console, playerX, playerY, '@', libtcod.BKGND_NONE)
        libtcod.console_blit(main_console, 0, 0, screen_width, screen_height, 0, 0, 0)

        #Draws console
        libtcod.console_flush()

        libtcod.console_put_char(main_console, playerX, playerY, ' ', libtcod.BKGND_NONE)
        action = handle_keys(key)

        move = action.get('move')
        exit = action.get('exit')

        #moves if action is move
        if move:
            moveX, moveY = move
            playerX += moveX
            playerY += moveY
        #exits if exit
        if exit:
            return True


if __name__ == '__main__':
    main()



