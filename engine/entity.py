import math
from random import randint

from engine.render_order import RenderOrder
from components.item import Item


class Entity:
    """
    Object representing players, monsters, items, etc.
    """

    def __init__(self, x, y, char, color, name,  blocks=False, render_order=RenderOrder.CORPSE, fighter=None,
                 inventory=None, item=None, ai=None, stairs=None, equipment=None, equippable=None):
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

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

        if self.item:
            self.item.owner = self

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

    def move_towards(self, target_x, target_y, game_map, entities):
        moveX = target_x - self.x
        moveY = target_y - self.y
        distance = math.sqrt(moveX ** 2 + moveY ** 2)

        moveX = int(round(moveX / distance))
        moveY = int(round(moveY / distance))

        if not (game_map.is_blocked(self.x + moveX, self.y + moveY) or
                get_blocking_entities_at_location(entities, self.x + moveX, self.y + moveY)):
            self.move(moveX, moveY)

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


