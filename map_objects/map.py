from engine.entity import Entity
from engine.item_functions import *
from engine.render_order import RenderOrder
from engine.random_utils import *
from components.ai import *
from components.equipment import EquipmentSlots
from components.equippable import Equippable
from components.fighter import Fighter
from components.item import Item
from components.stairs import Stairs
from map_objects.rectangle import Rect
from map_objects.tile import Tile
from random import randint
import tcod.bsp


class Map:
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_BSP_map(self, player, entities, map_width, map_height):
        # parameters for BSP splitting
        depth = 4
        min_width = 5
        min_height = 5
        hori_ratio = 1.5
        verti_ratio = 1.5
        # mess with seeds??

        # creates BSP tree and splits recursively with given parameters
        tree = tcod.bsp.BSP(x=5, y=3, width=map_width-5, height=map_height-5)
        tree.split_recursive(
            depth=depth,
            min_width=min_width,
            min_height=min_height,
            max_horizontal_ratio=hori_ratio,
            max_vertical_ratio=verti_ratio
        )
        # iterates through nodes creating rooms and hall ways
        self.create_BSP_rooms(player, tree, entities)

        # iterates through created rooms place monstas
        for node in tree.pre_order():
            if not node.children:
                self.place_bsp_entities(node, entities)

    def create_BSP_rooms(self, player, tree, entities):
        """Creates rooms from BSP leafs"""
        room_centers = []
        for node in tree.pre_order():
            # random height and width for rooms
            rand_width = randint(node.x + 4, (node.x + node.width-1))
            rand_height = randint(node.y + 4, (node.y + node.height-1))

            node.width = rand_width
            node.height = rand_height

            if not node.children:
                # creates rooms
                # adds center of node to be used for hallway mining
                center_x = int((rand_width + node.x)/2)
                center_y = int((rand_height + node.y)/2)
                room_centers.append([center_x,center_y])
                for x in range(node.x, node.width):
                    for y in range(node.y, node.height):
                        #if self.node_area_check(rand_height, rand_width, 10):  #Check if this is needed after we get the random room sizes working
                        self.tiles[x][y].block_sight = False
                        self.tiles[x][y].blocked = False

        for i in range(len(room_centers)):
            if i == 0:
                player.x , player.y = room_centers[i]

            s = randint(1, len(room_centers))
            if s == i:
                s_center_x, s_center_y = room_centers[s]
                stairs_component = Stairs(self.dungeon_level + 1)
                down_stairs = Entity(s_center_x, s_center_y , '>', libtcod.red, 'Stairs',
                                     render_order=RenderOrder.STAIRS, stairs=stairs_component)
                entities.append(down_stairs)

            x1, y1 = room_centers[i-1]
            x2, y2 = room_centers[i]

            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.tiles[x][y1].block_sight = False
                self.tiles[x][y1].blocked = False
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.tiles[max(x1,x2)][y].block_sight = False
                self.tiles[max(x1,x2)][y].blocked = False

    def place_bsp_entities(self, node, entities):
        """Handles monster gen"""
        max_monsters_per_room = from_dungeon_level([[4, 1], [3, 4], [5, 6]], self.dungeon_level)
        max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)
        number_of_monsters = randint(0, max_monsters_per_room)  # Gets rand num of spoopy monsters

        monster_chances = {
            'ashlee': 45,
            'orc': from_dungeon_level([[45, 3], [55, 5], [65, 7]], self.dungeon_level),
            'goblin': from_dungeon_level([[60, 3], [40, 5], [20, 7]], self.dungeon_level),
            'troll': from_dungeon_level([[0, 3], [20, 5], [30, 7]], self.dungeon_level)

        }

        item_chances = {
            'healing_potion': from_dungeon_level([[25, 4]], self.dungeon_level),
            'lighting_scroll': from_dungeon_level([[25, 3]], self.dungeon_level),
            'fireball_scroll': from_dungeon_level([[25, 2]], self.dungeon_level),
            'wand': from_dungeon_level([[15, 1]], self.dungeon_level)
        }

        for i in range(0,1):
            x = randint(node.x + 1, node.width - 1)
            y = randint(node.y + 1, node.height - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                world_obj_comp = Item(use_function=spell_tome)
                world_objects = Entity(x, y, '$', libtcod.dark_flame, 'spell_tome', render_order=RenderOrder.ITEM,
                                       item=world_obj_comp, interactable=True)

                entities.append(world_objects)

        for i in range(number_of_monsters):
            # Choose random location in the room
            x = randint(node.x + 1, node.width - 1)
            y = randint(node.y + 1, node.height - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                # Choose monsters randomly
                monster_choice = random_choice_from_dict(monster_chances)

                if monster_choice == 'ashlee':
                    monster_fight_comp = Fighter(hp=10, armor_class=3, strength=6)
                    ai_comp = BasicMonster()
                    monster = Entity(x, y, 'A', libtcod.purple, "Ashlee", blocks=True, fighter=monster_fight_comp,
                                     render_order=RenderOrder.ACTOR, ai=ai_comp)

                elif monster_choice == 'orc':
                    monster_fight_comp = Fighter(hp=10, armor_class=4, strength=5)
                    ai_comp = BasicMonster()
                    monster = Entity(x, y, 'O', libtcod.darkest_green, "Orc", blocks=True, fighter=monster_fight_comp,
                                     render_order=RenderOrder.ACTOR, ai=ai_comp)

                elif monster_choice == 'goblin':
                    monster_fight_comp = Fighter(hp=10, armor_class=2, strength=2)
                    ai_comp = BasicMonster()
                    monster = Entity(x, y, 'G', libtcod.dark_green, "Goblin", blocks=True, fighter=monster_fight_comp,
                                     render_order=RenderOrder.ACTOR, ai=ai_comp)
                    
                elif monster_choice == 'troll':
                    monster_fight_comp = Fighter(hp=15, armor_class=7, strength=10)
                    ai_comp = BasicMonster()
                    monster = Entity(x, y, 'T', libtcod.dark_green, "Troll", blocks=True, fighter=monster_fight_comp,
                                     render_order=RenderOrder.ACTOR, ai=ai_comp)

                try:
                    entities.append(monster)
                except UnboundLocalError:
                    pass
                # Handles item gen
            number_of_items = randint(0, max_items_per_room)

            for i in range(number_of_items):
                x = randint(node.x + 1, node.width - 1)
                y = randint(node.y + 1, node.height - 1)

                if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                    item_choice = random_choice_from_dict(item_chances)
                    if item_choice == 'healing_potion':
                        item_component = Item(use_function=heal, amount=5)
                        item = Entity(x, y, '!', libtcod.violet, 'Healing Potion', render_order=RenderOrder.ITEM,
                                      item=item_component)

                    elif item_choice == 'lightning_scroll':
                        item_component = Item(use_function=cast_lighting, damage=20, maximum_range=5)
                        item = Entity(x, y, '~', libtcod.yellow, 'Lightning Scroll', render_order=RenderOrder.ITEM,
                                      item=item_component)

                    elif item_choice == 'fireball_scroll':
                        item_component = Item(use_function=cast_fireball, targeting=True, targeting_message=Message(
                            'Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan),
                                              damage=15, radius=3)
                        item = Entity(x, y, '#', libtcod.red, 'Fireball Scroll', render_order=RenderOrder.ITEM,
                                      item=item_component)
                    elif item_choice == 'wand':
                        equippable_component = Equippable(EquipmentSlots.MAIN_HAND, intelligence_bonus=3)
                        item = Entity(x, y, '/', libtcod.red, 'Wand', equippable=equippable_component)

                    try:
                        entities.append(item)
                    except UnboundLocalError:
                        pass

    def node_area_check(self, height, width, wanted_area):
        """Checks height and width of node against desired area"""
        area = height * width
        if area > wanted_area:
            return True

        return False

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False

    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_BSP_map(player, entities, constants['map_width'], constants['map_height'])
        message_log.add_message(Message('The stairs crumble behind you', libtcod.light_violet))

        return entities
