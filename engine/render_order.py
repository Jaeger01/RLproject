from enum import Enum


class RenderOrder(Enum):
    # Higher number is higher render priority
    CORPSE = 1
    ITEM = 2
    STAIRS = 3
    ACTOR = 4
