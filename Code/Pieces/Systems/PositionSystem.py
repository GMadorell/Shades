# -*- coding: UTF-8 -*-
import larv
import helper
from pymunk.vec2d import Vec2d

from ..Components import PhysicsComponent
from ..Components import PositionComponent

class PositionSystem(larv.System):
    """
    Updates the position of all of those entities with a body that can move:
    They should all have:
        - PhysicsComponent
        - PositionComponent
    Simply sets every position correctly to their body.
    """
    def update(self):
        list_entities = self.group_manager.get('dynamic')
        if self.group_manager.doesGroupExist('moving_platform'):                
            list_entities += self.group_manager.get('moving_platform')

        for entity in list_entities:
            physics_comp = self.entity_manager.getComponent(entity, PhysicsComponent.__name__)
            position_comp = self.entity_manager.getComponent(entity, PositionComponent.__name__)

            x, y = physics_comp.shape.body.position
            position_comp.x = x
            position_comp.y = y
            position_comp.position = Vec2d(x,y)