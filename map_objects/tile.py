class Tile:
    """
    Map tiles with various properties
    """

    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        if block_sight is None:
            block_sight = blocked

        self.block_sight = block_sight
        self.explored = True  # controls whether you can see the whole map(unlighted) should be set to false
