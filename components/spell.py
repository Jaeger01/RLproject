class Spell:
    """
    Marks entity as spell
    """
    def __init__(self, cast_function=None, targeting=False, targeting_message=None, mana_cost=0, **kwargs):
        self.cast_function = cast_function
        self.function_kwargs = kwargs
        self.targeting = targeting
        self.targeting_message = targeting_message
        self.mana_cost = mana_cost

