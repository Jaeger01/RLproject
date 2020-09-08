from engine.game_messages import Message
import tcod as libtcod


class Grimoire:
    """
    Holds spells and handles spell use
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.spells = []

    def add_spell(self, spell):
        results = []

        if len(self.spells) >= self.capacity:
            results.append({
                'spell_added': None,
                'message': Message('You have no more spell slots remaining', libtcod.yellow)
            })
        else:
            results.append({
                'spell_added': spell,
                'message': Message('You have learned the secrets of the {0} spell'.format(spell.name), libtcod.blue)
            })

            self.spells.append(spell)

        return results

    def cast(self, spell_entity, **kwargs):
        results = []

        spell = spell_entity
        player_mana = kwargs.get('player_mana')

        if player_mana >= spell.function_kwargs.get('cost'):
            if spell.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                results.append({'targeting': spell_entity})

            else:
                kwargs = {**spell.function_kwargs, **kwargs}
                spell_cast_results = spell.cast_function(self.owner, **kwargs)
                results.extend(spell_cast_results)

        return results
