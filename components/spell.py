class Spell:
    """
    Marks entity as spell
    """
    def __init__(self, cast_function=None, targeting=False, targeting_message=None, **kwargs):
        self.cast_function = cast_function
        self.function_kwargs = kwargs
        self.targeting = targeting
        self.targeting_message = targeting_message


