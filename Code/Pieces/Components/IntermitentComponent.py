import larv


class IntermitentComponent(larv.Component):
    """
    Class used for those entities that need to be active only a partial amount
    of time.
    """
    def __init__(self, interval = 1500):
        self.time = None
        self.interval = interval # milliseconds