import larv
from LightEngine import Light
from ColorConstants import *

class LightComponent(larv.Component):
    """
    Holds info about a light structure.
    """
    def __init__(self, x, y, size = 100, alpha = None, color = WHITE):
        self.light = Light(x, y, size, alpha, color)
