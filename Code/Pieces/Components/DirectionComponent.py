import larv


class DirectionComponent(larv.Component):
    """
    Holds information about the direction which the entity will move, shoot
    to, etc.
    Direction can have the following values:
        - up
        - down
        - right
        - left
    """
    def __init__(self, direction):
        valid_options = ('up', 'down', 'right', 'left')
        assert direction in valid_options, '{0}'.format(direction)

        self.direction = direction


