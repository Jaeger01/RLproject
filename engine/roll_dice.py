from random import randint


def roll_dice(sides):
    damage = 0
    damage += randint(0, sides) + 1

    return damage
