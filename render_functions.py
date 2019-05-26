import tcod as libtcod
from enum import Enum


class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3

colors = {
    'dark_wall': libtcod.Color(0, 0, 25),
    'dark_ground': libtcod.Color(5, 10, 50),
    'light_wall': libtcod.Color(0, 0, 170),
    'light_ground': libtcod.Color(125, 170, 250)
}


def render_all(console, entities, player, fov_map, fov_recompute, map, screen_width, screen_height, colors):
    if fov_recompute:
        # Draws tiles in game map
        for y in range(map.height):
            for x in range(map.width):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        # libtcod.console_put_char_ex(console, x, y, '#', libtcod.blue, colors.get('dark_wall'))
                        libtcod.console_set_char_background(console, x, y, colors.get('light_wall'), libtcod.BKGND_SET)
                    else:
                        # libtcod.console_put_char_ex(console, x, y, '.', libtcod.blue, colors.get('dark_ground'))
                        libtcod.console_set_char_background(console, x, y, colors.get('light_ground'), libtcod.BKGND_SET)

                    map.tiles[x][y].explored = True

                elif map.tiles[x][y].explored:
                    if wall:
                        # libtcod.console_put_char_ex(console, x, y, '#', libtcod.blue, colors.get('dark_wall'))
                        libtcod.console_set_char_background(console, x, y, colors.get('dark_wall'), libtcod.BKGND_SET)
                    else:
                        # libtcod.console_put_char_ex(console, x, y, '.', libtcod.blue, colors.get('dark_ground'))
                        libtcod.console_set_char_background(console, x, y, colors.get('dark_ground'), libtcod.BKGND_SET)

    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)
    # Draws all entities in list and map
    for entity in entities_in_render_order:
        draw_entity(console, entity, fov_map)

    libtcod.console_set_default_foreground(console, libtcod.white)
    libtcod.console_print_ex(console, 1, screen_height - 2, libtcod.BKGND_NONE, libtcod.LEFT,
                             'HP: {0:02}/{1:02}'.format(player.fighter.hp, player.fighter.max_hp))

    libtcod.console_blit(console, 0, 0, screen_width, screen_height, 0, 0, 0)


def clear_all(console, entities):
    # Clears entities after drawing
    for entity in entities:
        clear_entity(console, entity)


def draw_entity(console, entity, fov_map):
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
        # Draws entities
        libtcod.console_set_default_foreground(console, entity.color)
        libtcod.console_put_char(console, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)


def clear_entity(console, entity):
    # Erase character  object
    libtcod.console_put_char(console, entity.x, entity.y, ' ', libtcod.BKGND_NONE)


# Fov functions
def initialize_fov(map):
    fov_map = libtcod.map_new(map.width, map.height)

    for y in range(map.height):
        for x in range(map.width):
            libtcod.map_set_properties(fov_map, x, y, not map.tiles[x][y].block_sight, not map.tiles[x][y].blocked)

    return fov_map


def recompute_fov(fov_map, x, y, radius, light_walls=True, algorithm=0):
    libtcod.map_compute_fov(fov_map, x, y, radius, light_walls, algorithm)

