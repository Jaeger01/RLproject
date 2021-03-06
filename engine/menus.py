import tcod as libtcod

from engine.descriptions import *
import textwrap


def menu(con, header, options, width, screen_width, screen_height, borders=False):
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options.')

    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, screen_height, header)
    height = len(options) + header_height + 1

    # create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    # print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 1, 1, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
    # print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 1, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    # blit the contents of "window" to the root console
    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)

    # Draws * borders around menus if borders is True
    if borders:
        for x_val in range(0, width):
            libtcod.console_put_char(window, x_val, 0, '*')
        for y_val in range(0, height):
            libtcod.console_put_char(window, 0, y_val, '*')
        for y_v in range(0, height):
            libtcod.console_put_char(window, width-1, y_v, '*')
        for x_v in range(0, width):
            libtcod.console_put_char(window, x_v, height-1, '*')

    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)


# Look menus are essentially large text boxes to display monster/item information
# Could be tweeked to be used as menus for displaying dialogue options and things
def look_menu(con, thing, screen_width, screen_height):
    width = 50
    height = 50
    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, screen_height, thing.name)

    # create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    # print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 1, 1, width, height, libtcod.BKGND_NONE, libtcod.LEFT, thing.name)
    mon_desc = get_monster_desc()
    item_desc = get_item_desc()
    spell_desc = get_spell_desc()
    y = header_height + 1

    # kinda a dumb loop maybe I should just make one big desc list to kill it?
    if thing.item:
        thing_text = item_desc[thing.name]
    elif thing.fighter:
        thing_text = mon_desc[thing.name]
    elif thing.spell:
        thing_text = spell_desc[thing.name]

    lined_mon_text = textwrap.wrap(thing_text, width - 2)
    for line in lined_mon_text:
        text = line
        libtcod.console_print_ex(window, 1, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1

    # blit the contents of "window" to the root console
    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)

    # Draws * borders around menus if borders is True
    for x_val in range(0, width):
        libtcod.console_put_char(window, x_val, 0, '*')
    for y_val in range(0, height):
        libtcod.console_put_char(window, 0, y_val, '*')
    for y_v in range(0, height):
        libtcod.console_put_char(window, width-1, y_v, '*')
    for x_v in range(0, width):
        libtcod.console_put_char(window, x_v, height-1, '*')

    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)


def inventory_menu(con, header, player, inventory_width, screen_width, screen_height):
    # Show a menu with each item of the inv as an option
    if len(player.inventory.items) == 0:
        options = ['Inventory is empty']
    else:
        options = []

        for item in player.inventory.items:
            if player.equipment.main_hand == item:
                options.append('{0}[E]'.format(item.name))
            else:
                options.append(item.name)

    menu(con, header, options, inventory_width, screen_width, screen_height, True)


def grimoire_menu(con, header, player, inventory_width, screen_width, screen_height):
    # Shows menu of spells currently in grimoire
    if len(player.grimoire.spells) == 0:
        options = ['You have no spells in your grimoire']
    else:
        options = []

        for spell in player.grimoire.spells:
            options.append(spell.name)

    menu(con, header, options, inventory_width, screen_width, screen_height, True)


def main_menu(con, background_image, screen_width, screen_height):
    libtcod.image_blit_2x(background_image, 0, 0, 0)

    libtcod.console_set_default_foreground(0, libtcod.yellow)
    libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height / 2) - 4, libtcod.BKGND_NONE, libtcod.CENTER,
                             'Tongue of the Ancients')
    # libtcod.console_print_ex(0, int(screen_width / 2), int(screen_height - 2), libtcod.BKGND_NONE, libtcod.CENTER,
    #                        'By (Your name here)')

    menu(con, ' ', ['Play a new game', 'Continue last game', 'Quit'], 24, screen_width, screen_height)


def message_box(con, header, width, screen_width, screen_height):
    menu(con, header, [], width, screen_width, screen_height)
