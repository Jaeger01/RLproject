class Spell:
    """
    Spell as non entity
    """
    def __init__(self,name, cast_function=None, targeting=False, targeting_message=None, is_spell=True,
                 item=False, **kwargs):
        self.cast_function = cast_function
        self.function_kwargs = kwargs
        self.targeting = targeting
        self.targeting_message = targeting_message
        self.is_spell = is_spell
        self.item = item
        self.name = name


