import tcod as libtcod
from engine.game_messages import Message


def lightning(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    maximum_range = kwargs.get('maximum_range')

    results = []

    target = None
    closest_dist = maximum_range + 1

    for entity in entities:
        if entity.fighter and entity != caster and libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
            distance = caster.distance_to(entity)

            if distance < closest_dist:
                target = entity
                closest_dist = distance

    if target:
        results.append({'target': target,
                        'message': Message('A lighting bolt strikes the {0} for {1} damage'.format(target.name,
                                                                                                   damage))})
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append({'target': None, 'message': Message('No enemy is close enough', libtcod.red)})

    return results


def fireball(*args, **kwargs):
    entites = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False, 'message': Message('You cannot see there!', libtcod.yellow)})
        return results

    results.append({'consumed': True, 'message': Message('The fireball explodes buring all within {0} tiles!'
                                                         .format(radius), libtcod.orange)})

    for entity in entites:
        if entity.distance(target_x, target_y) <= radius and entity.fighter:
            results.append({'message': Message('The {0} gets burned for {1} hit points!'.format(entity.name, damage),
                                               libtcod.orange)})
            results.extend(entity.fighter.take_damage(damage))

    return results