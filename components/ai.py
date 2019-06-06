import tcod as libtcod

"""
Holds AIs for monsters
"""


class BasicMonster:
    def take_turn(self, target, fov_map, game_map, entities):
        results = []

        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):

            if monster.distance_to(target) >= 2:
                monster.move_towards(target.x, target.y, game_map, entities)

            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)
        # If monsters don't see you they just move in a random direction
        else:
            monster.wander(game_map, entities)

        return results


