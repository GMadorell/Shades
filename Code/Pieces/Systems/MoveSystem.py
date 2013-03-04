# -*- coding: UTF-8 -*-
import larv

from ..Components import PhysicsComponent
from ..Components import MoveComponent
from ..Components import PositionComponent

from Globals import *

class MoveSystem(larv.System):
    """
    Takes every entity that has:
        - MoveComponent
        - PhysicsComponent
    and updates their velocity depending on move variables.
    """
    def __init__(self):
        self.previous_hero_y = 0
        self.previous_hero_y2 = 0
        self.count = 0

    def update(self):
        list_entities = self.entity_manager.getEntitiesHavingComponents(
                            PhysicsComponent.__name__,
                            MoveComponent.__name__)

        has_hero = self.group_manager.doesGroupExist('hero')
        if has_hero:
            hero = self.group_manager.get('hero')[0]

        for entity in list_entities:
            physics_comp = self.entity_manager.getComponent(entity, PhysicsComponent.__name__)
            move_comp = self.entity_manager.getComponent(entity, MoveComponent.__name__)

            move_right = move_comp.move_right
            move_left = move_comp.move_left
            move_up = move_comp.move_up
            move_down = move_comp.move_down
            mid_air = move_comp.mid_air

            # Process lateral movement
            # If the movement in that direction should be applied, we just add an
            # acceleration to that movement and see if we didn't surpass the limit.
            if move_right:
                desired_velocity = physics_comp.body.velocity.x + move_comp.x_acceleration
                desired_velocity = min(desired_velocity, move_comp.max_x_velocity)
                physics_comp.body.velocity.x = desired_velocity
            elif move_left:
                desired_velocity = physics_comp.body.velocity.x - move_comp.x_acceleration
                desired_velocity = max(desired_velocity, -move_comp.max_x_velocity)
                physics_comp.body.velocity.x = desired_velocity
            else:
                pass
                if not mid_air:
                    physics_comp.body.velocity = (0,physics_comp.body.velocity.y)

            # Process moving up/down status
            if move_up:
                # Update the vertical velocity, with a max
                desired_velocity = physics_comp.body.velocity.y + move_comp.y_acceleration
                desired_velocity = min(desired_velocity, move_comp.max_y_speed)
                physics_comp.body.velocity.y = desired_velocity
                # If we get to the maximum permitted speed, don't allow more
                if desired_velocity == move_comp.max_y_speed:
                    move_comp.move_up = False
            elif move_down:
                # Update the vertical velocity, with a max
                desired_velocity = physics_comp.body.velocity.y - move_comp.y_acceleration
                desired_velocity = max(desired_velocity, -move_comp.max_y_speed)
                physics_comp.body.velocity.y = desired_velocity
                # If we get to the maximum permitted speed, don't allow more
                if desired_velocity == move_comp.max_y_speed:
                    move_comp.move_down = False

            # if move_comp.mid_air and entity.id == hero.id:
            #     if physics_comp.shape.body.velocity.y > 1/2 * MAX_JUMP_SPEED:
            #         print('max jump speed', physics_comp.shape.body.velocity.y)
            #         self.count = 2

            # If y velocity is very low, won't be in mid air
            if physics_comp.body.velocity.y**2 > 0.01:
                move_comp.mid_air = True
            else:
                move_comp.mid_air = False

            if entity.id == hero.id:
                position_comp = self.entity_manager.getComponent(hero, PositionComponent.__name__)
                self.previous_hero_y2 = self.previous_hero_y
                self.previous_hero_y = position_comp.y