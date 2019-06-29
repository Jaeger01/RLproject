from engine.menus import *
from engine.game_states import *

colors = {
    'dark_wall': libtcod.Color(0, 0, 25),
    'dark_ground': libtcod.Color(5, 10, 50),
    'light_wall': libtcod.Color(0, 0, 170),
    'light_ground': libtcod.Color(125, 170, 250),
    'highlighted': libtcod.Color(230, 250, 60)
}


def render_all(console, panel, entities, player, fov_map, fov_recompute, message_log, game_map, screen_width,
               screen_height, bar_width, panel_height, panel_y, colors, game_state, mouse):

    if fov_recompute:
        # Draws tiles in game map
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        #libtcod.console_put_char_ex(console, x, y, '#', libtcod.blue, colors.get('light_wall'))
                        libtcod.console_set_char_background(console, x, y, colors.get('light_wall'), libtcod.BKGND_SET)
                    else:
                        #libtcod.console_put_char_ex(console, x, y, '.', libtcod.blue, colors.get('light_ground'))
                        libtcod.console_set_char_background(console, x, y, colors.get('light_ground'), libtcod.BKGND_SET)

                    game_map.tiles[x][y].explored = True

                elif game_map.tiles[x][y].explored:
                    if wall:
                        #libtcod.console_put_char_ex(console, x, y, '#', libtcod.blue, colors.get('dark_wall'))
                        libtcod.console_set_char_background(console, x, y, colors.get('dark_wall'), libtcod.BKGND_SET)
                    else:
                        #libtcod.console_put_char_ex(console, x, y, '.', libtcod.blue, colors.get('dark_ground'))
                        libtcod.console_set_char_background(console, x, y, colors.get('dark_ground'), libtcod.BKGND_SET)

    entities_in_render_order = sorted(entities, key=lambda z: z.render_order.value)
    # Draws all entities in list and map
    for entity in entities_in_render_order:
        draw_entity(console, entity, fov_map, game_map)

    libtcod.console_blit(console, 0, 0, screen_width, screen_height, 0, 0, 0)

    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    # Prints messages
    y = 1
    for message in message_log.messages:
        libtcod.console_set_default_foreground(panel, message.color)
        libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
        y += 1

    for x_val in range(bar_width+1, int(message_log.width/2)):
        libtcod.console_put_char(panel, x_val, 0, '*', libtcod.BKGND_NONE)
    for y_val in range(0, panel.height):
        libtcod.console_put_char(panel, int(message_log.width/2), y_val, '*', libtcod.BKGND_NONE)

    render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp,
               libtcod.darkest_red, libtcod.darker_red)
    libtcod.console_print_ex(panel, 1, panel_height - 2, libtcod.BKGND_NONE, libtcod.LEFT,
                             'Floor: {0}'.format(game_map.dungeon_level))
    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = 'Press the key next to an item to use it.\n'
        else:
            inventory_title = 'Press the key next to an item to drop it'

        inventory_menu(console, inventory_title, player, 50, screen_width, screen_height)

    if game_state == GameStates.LOOK:
        (x, y) = (mouse.cx, mouse.cy)
        for entity in entities:
            if entity.x == x and entity.y == y and libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
                mon = entity
                look_menu(console, mon, screen_width, screen_height)


def clear_all(console, entities):
    # Clears entities after drawing
    for entity in entities:
        clear_entity(console, entity)


def draw_entity(console, entity, fov_map, game_map):
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
        # Draws entities
        if libtcod.map_is_in_fov(fov_map, entity.x, entity.y) or (entity.stairs and game_map.tiles[entity.x][entity.y].
                                                                  explored):
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


def render_bar(panel, x, y, total_width, name, value, max, bar_color, back_color):
    bar_width = int(float(value) / max * total_width)

    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, panel.height - 1, bar_width, 1, False, libtcod.BKGND_SCREEN)
    libtcod.console_set_default_background(panel, bar_color)

    if bar_width > 0:
        libtcod.console_rect(panel, x, panel.height - 1, bar_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x, panel.height - 1, libtcod.BKGND_NONE, libtcod.LEFT,
                             '{0}: {1}/{2}'.format(name, value, max))
    for x_val in range(0, bar_width+1):
        libtcod.console_put_char(panel, x_val, 0, '*')
    for y_val in range(0, panel.height):
        libtcod.console_put_char(panel, bar_width+1, y_val, '*')
    for y_val in range(0, panel.height):
        libtcod.console_put_char(panel, 0, y_val, '*')


# Not working correctly, just paints everything. the paths don't disappear when the mouse is moved
def render_path(con, player, fov_map, target_x, target_y, path_color):
    # highlights path to mouse
    # (target_x, target_y) = (mouse.cx, mouse.cy)
    line = libtcod.line_iter(player.x, player.y, target_x, target_y)
    for x, y in line:
        if libtcod.map_is_in_fov(fov_map, x, y):
            libtcod.console_set_char_background(con, x, y, path_color, libtcod.BKGND_LIGHTEN)


