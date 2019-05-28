import math
import tcod as libtcod
from render_functions import RenderOrder


class Entity:
    """
    Object representing players, monsters, items, etc.
    """

    def __init__(self, x, y, char, color, name,  blocks=False, render_order=RenderOrder.CORPSE, fighter=None, ai=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
        self.ai = ai
        self.render_order = render_order

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

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


def get_blocking_entities_at_location(entities, destination_x, destination_y):
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity

    return None

