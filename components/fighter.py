import tcod as libtcod
from game_messages import Message


class Fighter:
    def __init__(self, hp, defense_value, attack_value):
        self.max_hp = hp
        self.hp = hp
        self.defense_value = defense_value
        self.attack_value = attack_value

    def take_damage(self, amount):
        results = []
        self.hp -= amount

        if self.hp <= 0:
            results.append({'dead': self.owner})
        return results

    def attack(self, target):
        results = []
        damage = self.attack_value - target.fighter.defense_value
        if damage > 0:
            results.append({'message': Message('{0} attacks {1} for {2} hit points.'.format(
                self.owner.name.capitalize(), target.name, str(damage)), libtcod.white)})
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({'message': Message('{0} attacks {1} but does no damage.'.format(
                self.owner.name.capitalize(), target.name), libtcod.white)})

        return results
