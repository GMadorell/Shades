import larv

class PhysicsComponent(larv.Component):
    """
    Holds info about a pymunk's shape and body structure.
    """
    def __init__(self, shape):
        self.shape = shape
        self.body = shape.body
