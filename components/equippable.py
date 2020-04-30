class Equippable:
    """
    Marks entity as something able to be equipped
    """
    def __init__(self, slot, intelligence_bonus=0, strength_bonus=0, armor_bonus=0, max_hp_bonus=0):
        self.slot = slot
        self.intelligence_bonus = intelligence_bonus
        self.strength_bonus = strength_bonus
        self.armor_bonus = armor_bonus
        self.max_hp_bonus = max_hp_bonus
