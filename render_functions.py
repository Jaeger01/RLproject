import tcod as libtcod


def render_all(console, entities, map, screen_width, screen_height, colors):
    # Draws tiles in game map
    for y in range(map.height):
        for x in range(map.width):
            wall = map.tiles[x][y].block_sight

            if wall:
                libtcod.console_set_char_background(console, x, y, colors.get('dark_wall'), libtcod.BKGND_SET)
                libtcod.console_set_char_foreground(console, x, y, libtcod.gray)
                libtcod.console_set_char(console, x, y, '#')
            else:
                libtcod.console_set_char_background(console, x, y, colors.get('dark_ground'), libtcod.BKGND_SET)
                libtcod.console_set_char_foreground(console, x, y, libtcod.white)
                libtcod.console_set_char(console, x, y, '.')

    # Draws all entities in list and map
    for entity in entities:
        draw_entity(console, entity)

    libtcod.console_blit(console, 0, 0, screen_width, screen_height, 0, 0, 0)


def clear_all(console, entities):
    # Clears entities after drawing
    for entity in entities:
        clear_entity(console, entity)


def draw_entity(console, entity):
    # Draws entities
    libtcod.console_set_default_foreground(console, entity.color)
    libtcod.console_put_char(console, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)


def clear_entity(console, entity):
    # Erase character  object
    libtcod.console_put_char(console, entity.x, entity.y, ' ', libtcod.BKGND_NONE)
