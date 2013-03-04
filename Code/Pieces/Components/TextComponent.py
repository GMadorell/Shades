import larv
import pygame

from ColorConstants import *

class TextComponent(larv.Component):
    """
    Class used for those components which should display text.
    """
    def __init__(self, color=WHITE, type='freesansbold.ttf', size=16):
        fontObj = pygame.font.Font('freesansbold.ttf', size) 
        self.surface = fontObj.render(text, True, color) # string, antialising, letter color, bg color