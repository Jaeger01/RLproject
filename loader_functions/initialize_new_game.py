import tcod as libtcod
from entity import Entity
from game_messages import MessageLog
from render_functions import RenderOrder

from Engine.game_states import GameStates
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from map_objects.map import Map


def get_constant_variables():
    window_title = 'RL project'

    screen_width = 150
    screen_height = 80

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 150
    map_height = 75

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    constant_variables = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius

    }

    return constant_variables


def get_game_variables(constant_variables):
    fighter_component = Fighter(hp=999, armor_value=3, attack_value=5)
    inventory_component = Inventory(26)
    equipment_component = Equipment()
    player = Entity(0, 0, '@', libtcod.red, 'Player', blocks=True, render_order=RenderOrder.ACTOR,
                    fighter=fighter_component, inventory=inventory_component, equipment=equipment_component)
    entities = [player]

    # Initializes map
    game_map = Map(constant_variables['map_width'], constant_variables['map_height'])
    game_map.make_map(constant_variables['max_rooms'], constant_variables['room_min_size'],
                      constant_variables['room_max_size'], constant_variables['map_width'],
                      constant_variables['map_height'], player, entities)

    # Initializes other game variables
    game_state = GameStates.PLAYERS_TURN
    message_log = MessageLog(constant_variables['message_x'], constant_variables['message_width'],
                             constant_variables['message_height'])

    return player, entities, game_map, game_state, message_log
