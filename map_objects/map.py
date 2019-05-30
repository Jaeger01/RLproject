import tcod as libtcod
from entity import Entity
from map_objects.tile import Tile
from map_objects.rectangle import Rect
from components.fighter import Fighter
from components.item import Item
from components.ai import *
from item_functions import *
from render_functions import RenderOrder
from random import randint


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities,
                 max_monsters_per_room, max_items_per_room):
        rooms = []
        num_rooms = 0
        for r in range(max_rooms):
            # Gets random height and width
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # Random position without going out of the boundaries of the map
            x = randint(0, map_width - w - 5)
            y = randint(0, map_height - h - 5)

            new_room = Rect(x, y, w, h)

            # Checks if rooms intersect
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # No intersection

                # Draws room tiles
                self.create_room(new_room)

                # center coordinates of the new room
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    player.x = new_x
                    player.y = new_y
                else:
                    # Connect rooms with tunnels

                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    if randint(0, 1) == 1:
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.place_entities(new_room, entities, max_monsters_per_room, max_items_per_room)
                rooms.append(new_room)
                num_rooms += 1

    def create_room(self, room):
        # Makes tiles in rect passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False

    def place_entities(self, room, entities, max_monsters_per_room, max_items_per_room):
        # Handles monster gen
        number_of_monsters = randint(0, max_monsters_per_room)  # Gets rand num of spoopy monsters

        for i in range(number_of_monsters):
            # Choose random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                # Choose monsters randomly
                monster_fight_comp = Fighter(hp=10, defense_value=3, attack_value=5)
                ai_comp = BasicMonster()
                monster = Entity(x, y, 'A', libtcod.purple, "Ashlee", blocks=True, fighter=monster_fight_comp,
                                 render_order=RenderOrder.ACTOR, ai=ai_comp)

                entities.append(monster)

        # Handles item gen
        number_of_items = randint(0, max_items_per_room)

        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                """item_component = Item(use_function=heal, amount=6)
                item = Entity(x, y, '!', libtcod.violet, 'Healing Potion', render_order=RenderOrder.ITEM,
                              item=item_component)
                item_component = Item(use_function=cast_lighting, damage=20, maximum_range=5)
                item = Entity(x, y, '~', libtcod.yellow, 'Lighting Scroll', render_order=RenderOrder.ITEM,
                              item=item_component)"""

                item_component = Item(use_function=cast_fireball, targeting=True, targeting_message=Message(
                    'Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan),
                                      damage=15, radius=3)
                item = Entity(x, y, '#', libtcod.red, 'Fireball Scroll', render_order=RenderOrder.ITEM,
                              item=item_component)
                entities.append(item)

