import tcod as libtcod
from engine.game_messages import Message
from engine.roll_dice import roll_dice


class Fighter:
    """
    Handles aspects of fighting an entity would do
    """
    def __init__(self, hp, armor_class, strength=0, intelligence=0, xp=0, mana=100):
        self.base_max_hp = hp
        self.hp = hp
        self.base_armor_class = armor_class
        self.base_strength = strength
        self.base_strength_mod = int((strength / 2) - 5)  # D&D modifier formula
        self.base_intelligence = intelligence
        self.base_intelligence_mod = int((intelligence / 2) -5)
        self.xp = xp
        self.max_mana = mana
        self.mana = mana

    def move(self):
        if self.mana < self.max_mana:
            self.mana += 1

    def take_damage(self, amount):
        results = []
        self.hp -= amount

        if self.hp <= 0:
            results.append({'dead': self.owner})
        return results

    def reduce_mana(self, amount):
        results = []
        self.mana -= amount

        if self.mana < 0:
            self.mana = 0
        return results

    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0
        return self.base_max_hp + bonus

    @property
    def strength(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.str_bonus
        else:
            bonus = 0
        return self.base_strength + bonus

    @property
    def intelligence(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.int_bonus
        else:
            bonus = 0
        return self.base_intelligence + bonus

    @property
    def strength_mod(self):
        return int((self.strength/2)-5)

    @property
    def intelligence_mod(self):
        return int((self.intelligence/2)-5)

    @property
    def armor_class(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.armor_bonus
        else:
            bonus = 0
        return self.base_armor_class + bonus

    def heal(self, amount):
        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, target):
        results = []
        damage = self.strength_mod + roll_dice(3) + roll_dice(3)
        # If you don't roll higher than their armor class your attack doesn't hit
        if roll_dice(20) < target.fighter.armor_class:
            results.append({'message': Message('{0} attacks {1} but the blow glances off'.format(
                self.owner.name.capitalize(), target.name), libtcod.white)})
        else:
            if damage > 0:
                results.append({'message': Message('{0} attacks {1} for {2} damage.'.format(
                    self.owner.name.capitalize(), target.name.capitalize(), str(damage)), libtcod.white)})
                results.extend(target.fighter.take_damage(damage))
            else:
                results.append({'message': Message('{0} attacks {1} but does no damage.'.format(
                    self.owner.name.capitalize(), target.name.capitalize()), libtcod.white)})

        return results
