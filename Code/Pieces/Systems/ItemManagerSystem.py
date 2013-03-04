import larv

from ..Components import PositionComponent
from ..Components import IntermitentComponent
from ..Components import DirectionComponent
from ..Components import StateComponent
from ..Components import PhysicsComponent
from ..Components import PathComponent

from pymunk.vec2d import Vec2d
from Globals import *

class ItemManagerSystem(larv.System):
    """
    This system will manage basic logic around the different items we can find in a
    level, such as:
        - Lasers (must have position, state, )
    It works using only the group manager for selecting entities, so it can
    always be added to any engine, even if that level doesn't have any item.
    """

    def update(self):
        # Find which elements does the level have
        has_lasers = self.group_manager.doesGroupExist('laser')
        has_moving_platforms = self.group_manager.doesGroupExist('moving_platform')
        has_camera = self.group_manager.doesGroupExist('camera')

        # Process the lasers.
        # If they are active, make them shoot in the direction they are setup 
        # to do so, then put them on inactive mode so they don't shoot every frame.
        if has_lasers:
            list_entities = self.group_manager.get('laser')
            for entity in list_entities:
                position_comp = self.entity_manager.getComponent(entity, PositionComponent.__name__)
                state_comp = self.entity_manager.getComponent(entity, StateComponent.__name__)
                direction_comp = self.entity_manager.getComponent(entity, DirectionComponent.__name__)
                if state_comp.state == 'active':
                    state_comp.state = 'inactive'
                    x, y = position_comp.x, position_comp.y
                    direction = direction_comp.direction
                    self.entity_factory.createLaserShot(x, y, direction)
                    # Make laser sound
                    LASER_SOUND.stop()
                    LASER_SOUND.play()

        if has_moving_platforms:
            list_entities = self.group_manager.get('moving_platform')
            for entity in list_entities:
                # print(1)
                # Get the information
                position_comp = self.entity_manager.getComponent(entity, PositionComponent.__name__)
                physics_comp = self.entity_manager.getComponent(entity, PhysicsComponent.__name__)                
                path_comp = self.entity_manager.getComponent(entity, PathComponent.__name__)
                index = path_comp.index
                path = path_comp.path

                # Get distance between destination and current position
                destination = Vec2d(path[index])
                # current = Vec2d(position_comp.x, position_comp.y)
                current = Vec2d(physics_comp.shape.body.position)
                distance = current.get_distance(destination)
                # print(current, destination, distance)
                # If we get there, go to next position
                if distance < MOVING_PLATFORM_SPEED:
                    # print(1)
                    # Adjust index to a legal value
                    path_comp.index += 1
                    path_comp.index %= len(path)
                    t = 1
                else: # advance
                    t = MOVING_PLATFORM_SPEED / distance
                new = current.interpolate_to(destination, t)
                physics_comp.shape.body.position = new
                physics_comp.shape.body.velocity = (new - current) / 1/FPS
                # print(new)









