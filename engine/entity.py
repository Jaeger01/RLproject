import math
from random import randint
import tcod as libtcod

from engine.render_order import RenderOrder
from components.item import Item


class Entity:
    """
    Object representing players, monsters, items, etc.
    """

    def __init__(self, x, y, char, color, name, steps=0, gix=1, blocks=False, render_order=RenderOrder.CORPSE, fighter=None,
                 inventory=None, item=None, ai=None, stairs=None, equipment=None, equippable=None, grimoire=None,
                 spell=None, interactable=False, world_object=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
        self.item = item
        self.inventory = inventory
        self.stairs = stairs
        self.ai = ai
        self.render_order = render_order
        self.equipment = equipment
        self.equippable = equippable
        self.grimoire = grimoire
        self.spell = spell
        self.steps = steps
        self.gix = 1 # This should be erased only here because I can't figure out how else to pass Grimoire menu index to render functions
        self.interactable = interactable
        self.world_object = world_object

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

        if self.item:
            self.item.owner = self

        if self.world_object:
            self.world_object.owner = self

        if self.spell:
            self.spell.owner = self

        if self.grimoire:
            self.grimoire.owner = self

        if self.inventory:
            self.inventory.owner = self

        if self.stairs:
            self.stairs.owner = self

        if self.equippable:
            self.equippable.owner = self
            if not self.item:
                item = Item()
                self.item = item
                self.item.owner = self

        if self.equipment:
            self.equipment.owner = self

    def move(self, moveX, moveY):
        # Moves entity
        self.x += moveX
        self.y += moveY
        self.steps += 1

    def move_towards(self, target_x, target_y, game_map, entities):
        moveX = target_x - self.x
        moveY = target_y - self.y
        distance = math.sqrt(moveX ** 2 + moveY ** 2)

        moveX = int(round(moveX / distance))
        moveY = int(round(moveY / distance))

        if not (game_map.is_blocked(self.x + moveX, self.y + moveY) or
                get_blocking_entities_at_location(entities, self.x + moveX, self.y + moveY)):
            self.move(moveX, moveY)

    def click_move(self, x, y, game_map, entities):
        line = libtcod.line_iter(self.x, self.y, x, y)
        skip_first = True
        for x, y in line:
            if skip_first:
                skip_first = False
            else:
                self.move_towards(x, y, game_map, entities)

    def move_astar(self, target, game_map, entities):
            # Create a FOV map that has the dimensions of the map
            fov = libtcod.map_new(game_map.width, game_map.height)

            # Scan the current map each turn and set all the walls as unwalkable
            for y1 in range(game_map.height):
                for x1 in range(game_map.width):
                    libtcod.map_set_properties(fov, x1, y1, not game_map.tiles[x1][y1].block_sight,
                                               not game_map.tiles[x1][y1].blocked)

            # Scan all the objects to see if there are objects that must be navigated around
            # Check also that the object isn't self or the target (so that the start and the end points are free)
            for entity in entities:
                if entity.blocks and entity != self and entity != target:
                    # Set the tile as a wall so it must be navigated around
                    libtcod.map_set_properties(fov, entity.x, entity.y, True, False)

            # Allocate a A* path
            # The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
            my_path = libtcod.path_new_using_map(fov, 1.41)

            # Compute the path between self's coordinates and the target's coordinates
            libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)

            # Check if the path exists, and in this case, also the path is shorter than 25 tiles
            # The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
            # It makes sense to keep path size relatively low to keep the monsters from running around the map if there's an alternative path really far away
            if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
                # Find the next coordinates in the computed full path
                x, y = libtcod.path_walk(my_path, True)
                if x or y:
                    # Set self's coordinates to the next path tile
                    self.x = x
                    self.y = y
            else:
                # Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
                # it will still try to move towards the player (closer to the corridor opening)
                self.move_towards(target.x, target.y, game_map, entities)

                # Delete the path to free memory
            libtcod.path_delete(my_path)

    """" Checks if object is next to player"""
    def is_next_to(self,object):
        if object.x == self.x-1 and object.y == self.y-1:
            return True
        elif object.x == self.x and object.y == self.y-1:
            return True
        elif object.x == self.x+1 and object.y == self.y-1:
            return True
        elif object.x == self.x-1 and object.y == self.y:
            return True
        elif object.x == self.x+1 and object.y == self.y:
            return True
        elif object.x == self.x-1 and object.y == self.y+1:
            return True
        elif object.x == self.x and object.y == self.y+1:
            return True
        elif object.x == self.x+1 and object.y == self.y+1:
            return True
        else:
            return False

    def distance_to(self, other):
        moveX = other.x - self.x
        moveY = other.y - self.y
        return math.sqrt(moveX ** 2 + moveY ** 2)

    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def wander(self, game_map, entities):
        # Makes monsters move random direction
        move_x = randint(-1, 1)
        move_y = randint(-1, 1)
        if not (game_map.is_blocked(self.x + move_x, self.y + move_y) or
                get_blocking_entities_at_location(entities, self.x + move_x, self.y + move_y)):
            self.x += move_x
            self.y += move_y
        else:  # If the tile is blocking recall until it finds a tile that isn't
            self.wander(game_map, entities)


def get_blocking_entities_at_location(entities, destination_x, destination_y):
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity

    return None


