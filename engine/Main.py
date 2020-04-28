from engine.death_functions import *
from engine.game_messages import *
from engine.render_functions import *
from engine.input_handlers import *
from loader_functions.data_loaders import *
from loader_functions.initialize_new_game import *
from engine.entity import *


def main():
    constant_variables = get_constant_variables()

    # Sets fonts root console
    libtcod.console_set_custom_font('arial12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(constant_variables['screen_width'], constant_variables['screen_height'],
                              constant_variables['window_title'], False, libtcod.RENDERER_SDL2)

    # Initializes consoles
    main_console = libtcod.console_new(constant_variables['screen_width'], constant_variables['screen_height'])
    panel = libtcod.console_new(constant_variables['screen_width'], constant_variables['panel_height'])

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = libtcod.image_load('menu_background.png')

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            main_menu(main_console, main_menu_background_image, constant_variables['screen_width'],
                      constant_variables['screen_height'])

            if show_load_error_message:
                message_box(main_console, 'No save game to load', 40, constant_variables['screen_width'],
                            constant_variables['screen_height'])

            libtcod.console_flush()

            action = handle_main_menu(key)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
            elif new_game:
                player, entities, game_map, game_state, message_log = get_game_variables(constant_variables)
                game_state = GameStates.PLAYERS_TURN

                show_main_menu = False
            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break

        else:
            libtcod.console_clear(main_console)
            play_game(player, entities, game_map, message_log, game_state, main_console, panel, constant_variables)

            show_main_menu = True


def play_game(player, entities, game_map, message_log, game_state, main_console, panel, constant_variables):
    # Initializes all main game variables
    prev_game_state = game_state
    fov_recompute = True
    fov_map = initialize_fov(game_map)
    key = libtcod.Key()
    mouse = libtcod.Mouse()
    targeting_item = None

    # Game Loop
    while not libtcod.console_is_window_closed():
        fps = libtcod.sys_get_fps()
        steps = player.steps
        libtcod.console_print_ex(main_console, 0, 0, libtcod.BKGND_NONE, libtcod.LEFT, 'FPS: {0}'.format(fps))
        libtcod.console_print_ex(main_console, 10, 0, libtcod.BKGND_NONE, libtcod.LEFT, 'steps: {0}'.format(steps))

        # Captures events
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        # Computes fov
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constant_variables['fov_radius'])

        # Draws all entities, maps, and UI
        render_all(main_console, panel, entities, player, fov_map, fov_recompute, message_log, game_map,
                   constant_variables['screen_width'],
                   constant_variables['screen_height'], constant_variables['bar_width'],
                   constant_variables['panel_height'],
                   constant_variables['panel_y'], colors, game_state, mouse)

        fov_recompute = False  # Don't want to recompute unnecessarily

        libtcod.console_flush()

        clear_all(main_console, entities)

        # Action handling
        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse, game_state)

        # Keys
        move = action.get('move')
        wait = action.get('wait')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        inventory_index = action.get('inventory_index')
        grimoire_index = action.get('grimoire_index')
        drop_inventory = action.get('drop_inventory')
        take_stairs = action.get('take_stairs')
        looking = action.get('looking')
        interacting = action.get('interact')
        exit = action.get('exit')

        # Mouse
        move_click = mouse_action.get('move')  # For move clicking but it's of course not working rn
        target_click = mouse_action.get('target_click')
        right_click = mouse_action.get('right_click')

        # Does player turn
        player_turn_results = []
        if move and game_state == GameStates.PLAYERS_TURN:

            # Regens mana each step
            if player.fighter.mana < player.fighter.max_mana:
                player.fighter.mana += 1

            moveX, moveY = move
            destination_x = player.x + moveX
            destination_y = player.y + moveY

            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)
                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(moveX, moveY)
                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

        # Handles pickups
        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)

                    break
            else:
                message_log.add_message(Message('There is nothing to get', libtcod.yellow))

        elif wait:
            game_state = GameStates.ENEMY_TURN
            # Regens mana each step
            if player.fighter.mana < player.fighter.max_mana:
                player.fighter.mana += 1


        if looking:
            prev_game_state = GameStates.PLAYERS_TURN
            game_state = GameStates.LOOK
            message_log.add_message(Message('Mouse over a tile to look at it.', libtcod.purple))

        if show_inventory:
            prev_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            prev_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if inventory_index is not None and prev_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]
            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if grimoire_index is not None and game_state == GameStates.PLAYERS_TURN:
            try:
                spell = player.grimoire.spells[grimoire_index]
            except IndexError:
                message_log.add_message(Message(('There\'s no spell in that slot'),libtcod.red))
                continue
            player_turn_results.extend(player.grimoire.cast(spell, entities=entities, fov_map=fov_map, player_mana = player.fighter.mana))

        if game_state == GameStates.TARGETING:
            item_use_results = None
            if target_click:
                target_x, target_y = target_click
                if targeting_item.item:
                    item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                                                            target_x=target_x, target_y=target_y)
                elif targeting_item.spell:
                    item_use_results = player.grimoire.cast(targeting_item, entities=entities, fov_map=fov_map,
                                                            player_mana=player.fighter.mana, target_x=target_x, target_y=target_y)

                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if take_stairs and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.stairs and entity.x == player.x and entity.y == player.y:
                    entities = game_map.next_floor(player, message_log, constant_variables)
                    fov_map = initialize_fov(game_map)
                    fov_recompute = True
                    libtcod.console_clear(main_console)
                    break

        if interacting:
            for entity in entities:
                if entity.interactable and player.is_next_to(entity) and entity.fighter != True:
                    if entity.name == 'spell_tome':
                        pickup_results = player.inventory.add_item(entity)
                        player_turn_results.extend(pickup_results)



        # Exits if exit
        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.LOOK):
                game_state = prev_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                save_game(player, entities, game_map, message_log, game_state)
                return True

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            spell_added = player_turn_result.get('spell_added')
            targeting = player_turn_result.get('targeting')
            equip = player_turn_result.get('equip')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')
            looked = player_turn_result.get('looked')
            spell_tome = player_turn_result.get('spell_tome')
            if message:
                message_log.add_message(message)

            if targeting_cancelled:
                game_state = prev_game_state

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            # Handles pickup/consume
            if item_added:
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if item_dropped:
                entities.append(item_dropped)
                game_state == GameStates.ENEMY_TURN

            if spell_tome:
                spell_comp = Spell(cast_function=lightning, damage=15 + player.fighter.intelligence_mod, maximum_range = 5, cost=25)
                spell = Entity(0, 0, '~', libtcod.dark_yellow, 'lightning', spell=spell_comp)
                player.grimoire.add_spell(spell)

            if spell_added:
                game_state = GameStates.ENEMY_TURN

            if targeting:
                prev_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING
                targeting_item = targeting
                if targeting_item.item:
                    message_log.add_message(targeting_item.item.targeting_message)
                if targeting_item.spell:
                    message_log.add_message(targeting_item.spell.targeting_message)

            if looked:
                game_state = prev_game_state
                message_log.add_message(Message('looked'))

            if equip:
                equip_results = player.equipment.toggle_equip(equip)

                for equip_result in equip_results:
                    equipped = equip_result.get('equipped')
                    dequipped = equip_result.get('dequipped')

                    if equipped:
                        message_log.add_message(Message('You equipped the {0}'.format(equipped.name)))
                    if dequipped:
                        message_log.add_message(Message('You dequipped the {0}'.format(dequipped.name)))

                game_state = GameStates.ENEMY_TURN

        # Does enemy turn
        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
    main()
