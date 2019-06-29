import tcod as libtcod
from engine.game_messages import Message
from engine.roll_dice import roll_dice


class Fighter:
    """
    Handles aspects of fighting an entity would do
    """
    def __init__(self, hp, armor_class, strength, intelligence=0, xp=0):
        self.base_max_hp = hp
        self.hp = hp
        self.armor_class = armor_class
        self.strength = strength
        self.strength_mod = int((strength / 2) - 5)  # D&D modifier formula
        self.intelligence = intelligence
        self.intelligence_mod = int((intelligence-2)-5)
        self.xp = xp

    def take_damage(self, amount):
        results = []
        self.hp -= amount

        if self.hp <= 0:
            results.append({'dead': self.owner})
        return results

    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0
        return self.base_max_hp + bonus

    @property
    def power(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.power_bonus
        else:
            bonus = 0
        return self.strength + bonus

    @property
    def defense(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.armor_bonus
        else:
            bonus = 0
        return self.armor_class + bonus

    def heal(self, amount):
        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, target):
        results = []
        damage = self.strength_mod + roll_dice(6) + roll_dice(6)
        # If you don't roll higher than their armor class your attack doesn't hit
        if roll_dice(20) < target.fighter.armor_class:
            results.append({'message': Message('{0} attacks {1} but the blow glances off'.format(
                self.owner.name.capitalize(), target.name), libtcod.white)})
        else:
            if damage > 0:
                results.append({'message': Message('{0} attacks {1} for {2} hit points.'.format(
                    self.owner.name.capitalize(), target.name, str(damage)), libtcod.white)})
                results.extend(target.fighter.take_damage(damage))
            else:
                results.append({'message': Message('{0} attacks {1} but does no damage.'.format(
                    self.owner.name.capitalize(), target.name), libtcod.white)})

        return results
