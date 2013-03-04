import larv


class PathComponent(larv.Component):
    """
    Entities that must support a path (like moving platforms) need to have this
    component.
    """
    def __init__(self, path, index = 0):
        """
        @path: list or touple of coordinate tuples [(100,100), (200,200)]
        @index: first index to be evaluated of the tuple.
        """
        self.path = path
        self.index = index

        self.initial_index = index