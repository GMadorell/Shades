import larv
from LightEngine import Light
from Raycast import Raycast
from ColorConstants import *

class LightComponent(larv.Component):
    """
    Holds info about a light structure.
    """
    def __init__(self, size = 200, alpha = 255, color = WHITE):
        self.light = Raycast()
        self.size = size
        self.alpha = alpha
        self.color = color