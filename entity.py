class Entity:
    """
    Object representing players, monsters, items, etc.
    """

    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, moveX, moveY):
        #Moves entity
        self.x += moveX
        self.y += moveY
