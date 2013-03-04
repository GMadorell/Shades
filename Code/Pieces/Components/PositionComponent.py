# -*- coding: UTF-8 -*-
import larv
import pymunk
from pymunk.vec2d import Vec2d

class PositionComponent(larv.Component):
    """
    x and y are standarized coordinates,
    but the rect should be in pygame's.
    """
    def __init__(self, x, y, rect = None):
        self.x = x
        self.y = y
        # self.position = Vec2d(x, y)
        self.rect = rect

        self.initial_x = x
        self.initial_y = y
