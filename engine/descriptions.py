
def get_monster_desc():

    monster_desc = {                                                                                          # line lim
        'Ashlee': 'A being so beautiful nothing can rival her majesty. Said to lure men with womanly charm'
                  ' and kill with a cold stare.',

        'Orc': 'Tall, tusked, and gray. It wields a brutal looking great-axe and'
               ' is covered in leather armor draped in furs. One must always be careful when Orcs are about.',

        'Goblin': 'Standing roughly three feet tall with yellow green skin Goblins are weak alone, '
                  'but can be a serious threat in large number. Armed with whatever it can find and '
                  'donning leathers, Goblins use any means necessary to achieve victory and care nothing '
                  'for the concept of honor. Many arrogant adventurers have fallen prey to the likes of Goblins.',

        # Descriptions of obelisks

        'Obelisk of the Start': 'Before you lies the ruins of [vakavan city], tainted by a foul presence. Go forth '
                                'and learn of the VaKavan and rid the ruins of the evil that grips it.'
                                '//WIP//',

        'Obelisk': "example text hererere"


    }

    return monster_desc


def get_item_desc():
    item_desc = {
        'Healing Potion': 'Tastes like a strawberry milkshake. Restores 15 HP',

        'Lightning Scroll': 'Glowing runes on old parchment. Produces a bolt of lightning when read aloud',

        'Fireball Scroll': 'Glowing runes on old parchment. Produces a ball of flame when read aloud',

        'Wand': 'A wand made from [insert wood type here]. '
                'Int +3',

        'Wooden Club': 'A club made from wood that\'s hard as stone. The club is flat and about 8 inches wide. It '
                       'narrows down into a carved handle ending in a rounded blunt pommel. The face of the club '
                       'is covered in carvings.'
                       'Strength +3',

        'Simple Robes': 'Simple set of robes woven from what looks likes some sort of wool. You can feel trace '
                        'amounts of magic residing in them. Int +3',

        'Vine Mail': 'Intricately woven vines resembling chain mail. They may look like ordinary vines but are '
                     'as strong as iron and much lighter. Worn by common VaKavan warriors.'

    }

    return item_desc


def get_spell_desc():
    spell_desc = {
        'Fireball': 'Type: Area of Effect                                                                           '
                    'Cost: 10 Mana                                                                                  '
                    'Radius: 3                                                                                      '
                    'Damage: 10                                                                                     '
                    'The caster ignites air into an exploding ball of flame to throw. Caution hot.',

        'Lightning': 'Type: Single Target                                                                           '
                     'Cost: 20 Mana                                                                                 '
                     'Range: 5                                                                                      '           
                     'Damage: 15                                                                                    '
                     'The caster discharges bolts of electricity from their fingertips. The wild nature of lightning'
                     'makes this spell impossible to aim simply grounding itself through the nearest foe. ',

    }

    return spell_desc
