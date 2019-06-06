class Equippable:
    """
    Marks entity as something able to be equipped
    """
    def __init__(self, slot, power_bonus=0, armor_bonus=0, max_hp_bonus=0):
        self.slot = slot
        self.power_bonus = power_bonus
        self.armor_bonus = armor_bonus
        self.max_hp_bonus = max_hp_bonus
