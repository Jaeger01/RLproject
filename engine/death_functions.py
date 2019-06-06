import tcod as libtcod
from engine.game_messages import Message
from engine.render_order import RenderOrder

from engine.game_states import GameStates


def kill_player(player):
    player.char = '%'
    player.color = libtcod.dark_red

    return Message('You died!', libtcod.red), GameStates.PLAYER_DEAD


def kill_monster(monster):
    death_message = Message('{0} has died!'.format(monster.name.capitalize()), libtcod.orange)

    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = False
    monster.name = 'Remains of ' + monster.name
    monster.render_order = RenderOrder.CORPSE

    return death_message
