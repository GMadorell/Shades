# -*- coding: UTF-8 -*-
import pygame

import larv
import helper
from Pieces.Components import *

from Globals import *
from ColorConstants import *

class LevelEntityFactory(larv.EntityFactory):
    """
    Used for creating entities.
    """
    def createHero(self, x, y):
        sprite = pygame.image.load('Images/placeholder.png').convert_alpha()

        shape = helper.createShapeBodyFromImage(sprite, x = x, y = y, mass = 100, 
                                                mode = 'dynamic', rotable=False,
                                                centered = True)
        shape.collision_type = HERO_C_TYPE
        # shape.friction = STD_FRICTION

        new_entity = self.entity_manager.createEntity()

        new_position_component = PositionComponent(x,y,sprite.get_rect())
        new_render_component = RenderComponent(sprite)        
        new_physics_component = PhysicsComponent(shape)
        new_move_component = MoveComponent(max_x_velocity = MAX_X_VELOCITY,
                                           x_acceleration = X_ACCELERATION,
                                           max_y_speed = MAX_JUMP_SPEED,
                                           y_acceleration = JUMP_ACCELERATION)
        new_state_component = StateComponent('alive')

        self.entity_manager.addComponent(new_entity, new_position_component)
        self.entity_manager.addComponent(new_entity, new_render_component)
        self.entity_manager.addComponent(new_entity, new_physics_component)
        self.entity_manager.addComponent(new_entity, new_move_component)
        self.entity_manager.addComponent(new_entity, new_state_component)

        self.group_manager.add(new_entity, 'hero')
        self.group_manager.add(new_entity, 'dynamic')
        return new_entity

    def createCamera(self):
        new_entity = self.entity_manager.createEntity()

        new_position_component = PositionComponent(0,0)

        self.entity_manager.addComponent(new_entity, new_position_component)

        self.group_manager.add(new_entity, 'camera')
        return new_entity

    def createLevelInfo(self, camera_x_limit_right = 0, camera_x_limit_left = 0,
                        camera_y_limit_top = 0, camera_y_limit_bottom = 0,
                        player_start = 0, player_finish = 0, level_name = ''):
        ## WARNING: We must multiply the y limits by -1 (get them negative),
        ##   else the calculations for the camera movement won't work.
        ##   If by any means camera limits should be negative, then
        ##   the whole camera system may not work.
        camera_y_limit_top *= -1
        camera_y_limit_bottom *= -1

        new_entity = self.entity_manager.createEntity()

        new_levelinfo_component = LevelInfoComponent()
        new_levelinfo_component.camera_x_limit_right = camera_x_limit_right
        new_levelinfo_component.camera_x_limit_left = camera_x_limit_left
        new_levelinfo_component.camera_y_limit_top = camera_y_limit_top
        new_levelinfo_component.camera_y_limit_bottom =  camera_y_limit_bottom
        if player_start:
            new_levelinfo_component.player_start = player_start
        if player_finish:
            new_levelinfo_component.player_finish = player_finish
        new_levelinfo_component.level_name = level_name

        self.entity_manager.addComponent(new_entity, new_levelinfo_component)

        self.group_manager.add(new_entity, 'level_info')
        return new_entity

    def createTerrain(self, x, y, sprite):
        """
        @x,y: standarized.
        """
        new_entity = self.entity_manager.createEntity()

        sprite.convert_alpha() # the image will be faster to blit

        width, height = sprite.get_size()
        x = x + width//2
        y = y - height//2

        new_position_component = PositionComponent(x, y, sprite.get_rect())
        new_render_component = RenderComponent(sprite)

        self.entity_manager.addComponent(new_entity, new_position_component)
        self.entity_manager.addComponent(new_entity, new_render_component)

        self.group_manager.add(new_entity, 'terrain')
        return new_entity

    def createRenderOnly(self, x, y, sprite):
        """
        @x,y: standarized.
        """
        new_entity = self.entity_manager.createEntity()

        new_position_component = PositionComponent(x, y, sprite.get_rect())
        new_render_component = RenderComponent(sprite)

        self.entity_manager.addComponent(new_entity, new_position_component)
        self.entity_manager.addComponent(new_entity, new_render_component)

        return new_entity

    def createCollision(self, x, y, width, height):
        """
        @x,y: standarized.
        """
        new_entity = self.entity_manager.createEntity()

        shape = helper.createCollision(x, y, width, height)
        shape.friction = STD_FRICTION
        shape.collision_type = COLLISION_C_TYPE
        new_physics_component = PhysicsComponent(shape)

        self.entity_manager.addComponent(new_entity, new_physics_component)

        self.group_manager.add(new_entity, 'collision')
        return new_entity

    def createDeathZone(self, x, y, width, height):
        """
        Creates an invisible entity which is a rectangle.
        Used for detecting zones the player shouldn't be and thus making him
        die if he gets into any of those zones.
        @x,y: standarized.
        """
        new_entity = self.entity_manager.createEntity()

        shape = helper.createCollision(x, y, width, height)
        shape.collision_type = ENEMY_C_TYPE

        new_physics_component = PhysicsComponent(shape)

        self.entity_manager.addComponent(new_entity, new_physics_component)

        self.group_manager.add(new_entity, 'death_zone')
        return new_entity    

    ### LIGHT
    def createLight(self, x, y, size = 100, alpha = None, color = WHITE):
        """
        @x,y: should be pygame coordinates
        @size: radius of the light
        @alpha: transparency, must be between 1 and 255
        """
        new_entity = self.entity_manager.createEntity()

        new_light_component = LightComponent(x, y, size, alpha, color)
        new_state_component = StateComponent('active')

        self.entity_manager.addComponent(new_entity, new_light_component)
        self.entity_manager.addComponent(new_entity, new_state_component)

        self.group_manager.add(new_entity, 'light')
        return new_entity

    def createIntermitentLight(self, x, y, size = 100, alpha = None, color = WHITE, interval=1500):
        """
        @x,y: should be pygame coordinates
        @size: radius of the light
        @alpha: transparency, must be between 1 and 255
        @interval: miliseconds to be turned on/off
        """
        new_entity = self.entity_manager.createEntity()

        new_light_component = LightComponent(x, y, size, alpha, color)
        new_state_component = StateComponent('active')
        new_intermitent_component = IntermitentComponent(interval)

        self.entity_manager.addComponent(new_entity, new_light_component)
        self.entity_manager.addComponent(new_entity, new_state_component)
        self.entity_manager.addComponent(new_entity, new_intermitent_component)

        self.group_manager.add(new_entity, 'light')
        self.group_manager.add(new_entity, 'intermitent')
        return new_entity

    def createObstructor(self, x, y, width, height):
        """
        @x, y: real coordinates (will be translated)
        """
        new_entity = self.entity_manager.createEntity()

        pyg_x, pyg_y = helper.xyToPygame(x, y) 
        rect = pygame.Rect(pyg_x, pyg_y, width, height)

        new_position_component = PositionComponent(x, y, rect)

        self.entity_manager.addComponent(new_entity, new_position_component)

        self.group_manager.add(new_entity, 'obstructor')
        return new_entity

    ### ITEMS
    def createIntermitentLaser(self, x, y, interval, direction):
        """
        @x, y: coordinates, standarized
        @interval: in milliseconds, rate of fire
        @direction: can be top, down, right or left, direction where it will fire
        """
        new_entity = self.entity_manager.createEntity()

        new_position_component = PositionComponent(x,y)
        new_state_component = StateComponent('active')
        new_intermitent_component = IntermitentComponent(interval)
        new_direction_component = DirectionComponent(direction)

        self.entity_manager.addComponent(new_entity, new_position_component)
        self.entity_manager.addComponent(new_entity, new_state_component)
        self.entity_manager.addComponent(new_entity, new_intermitent_component)
        self.entity_manager.addComponent(new_entity, new_direction_component)

        self.group_manager.add(new_entity, 'laser')
        return new_entity

    def createPermanentLaser(self, x, y, direction):
        """
        NOT WELL IMPLEMENTED.
        Just creates an intermitent laser with a very low interval.
        @x, y: coordinates, standarized
        @direction: can be top, down, right or left, direction where it will fire
        """
        return self.createIntermitentLaser(x, y,
                                           interval = PERMANENT_LASER_INTERVAL,
                                           direction = direction)

    def createLaserShot(self, x, y, direction):
        """
        @x, y: standarized coordinates
        @direction: can be top, down, right or left, direction where it will travel
        """
        sprite = pygame.image.load('Images/laser_shot.png').convert_alpha()

        shape = helper.createShapeBodyFromImage(sprite, x = x, y = y, mass = 1, 
                                                mode = 'dynamic', rotable=False,
                                                centered = True)
        shape.collision_type = SHOT_C_TYPE
        shape.group = LASER_GROUP

        # Override velocity function so it doesn't get affected by gravity
        def vel_function(body, gravity, damping, dt):
            pass
        shape.body.velocity_func = vel_function

        new_entity = self.entity_manager.createEntity()

        new_position_component = PositionComponent(x,y,sprite.get_rect())
        new_render_component = RenderComponent(sprite)        
        new_physics_component = PhysicsComponent(shape)
        new_move_component = MoveComponent(max_x_velocity = LASER_MAX_VELOCITY,
                                           x_acceleration = LASER_ACCELERATION,
                                           max_y_speed = LASER_MAX_VELOCITY,
                                           y_acceleration = LASER_ACCELERATION)
        # Switch direction to allow movement
        if direction == 'up':
            new_move_component.move_up = True
        elif direction == 'down':
            new_move_component.move_down = True
        elif direction == 'right':
            new_move_component.move_right = True
        elif direction == 'left':
            new_move_component.move_left = True
        else: raise ValueError()

        self.entity_manager.addComponent(new_entity, new_position_component)
        self.entity_manager.addComponent(new_entity, new_render_component)
        self.entity_manager.addComponent(new_entity, new_physics_component)
        self.entity_manager.addComponent(new_entity, new_move_component)

        self.group_manager.add(new_entity, 'laser_shot')
        self.group_manager.add(new_entity, 'dynamic')
        return new_entity

    def createCrate(self, x, y, sprite):
        sprite.convert_alpha()

        shape = helper.createShapeBodyFromImage(sprite, x = x, y = y, mass = 100, 
                                                mode = 'dynamic', rotable=False,
                                                centered = False)
        shape.collision_type = MOVABLE_C_TYPE
        shape.friction = STD_FRICTION

        new_entity = self.entity_manager.createEntity()

        new_position_component = PositionComponent(x,y,sprite.get_rect())
        new_render_component = RenderComponent(sprite)        
        new_physics_component = PhysicsComponent(shape)

        self.entity_manager.addComponent(new_entity, new_position_component)
        self.entity_manager.addComponent(new_entity, new_render_component)
        self.entity_manager.addComponent(new_entity, new_physics_component)

        self.group_manager.add(new_entity, 'dynamic')
        self.group_manager.add(new_entity, 'dynamic_obstructor')
        return new_entity

    def createMovingPlatform(self, x, y, path, sprite):
        """
        Creates a platform that will follow a path.
        @x,y: standarized coordinates
        @path: list of tuple of standarized coordinates [(100,100),(200,200)]
        @sprite: pygame.surface instance
        """        
        sprite.convert_alpha()
        # shape = helper.createShapeBodyFromImage(sprite, x = x, y = y, mass=pymunk.inf, 
        #                                         mode = 'dynamic', rotable=False,
        #                                         centered = True)
        body = pymunk.Body(pymunk.inf, pymunk.inf)
        body.position = x, y
        height = sprite.get_height()
        width = sprite.get_width()
        top_left =     (-width//2, -height//2)
        top_right =    ( width//2, -height//2)
        bottom_left =  (-width//2,  height//2)
        bottom_right = ( width//2,  height//2)
        vertices = (top_left, top_right, bottom_right, bottom_left)
        shape = pymunk.Poly(body, vertices)
        # shape.collision_type = COLLISION_C_TYPE
        shape.collision_type = MOVING_PLATFORM_C_TYPE
        # shape.friction = STD_FRICTION
        shape.friction = 1
        SPACE.add(shape)

        # Override velocity function so it doesn't get affected by gravity
        def vel_function(body, gravity, damping, dt):
            pass
        shape.body.velocity_func = vel_function

        new_entity = self.entity_manager.createEntity()

        new_path_component = PathComponent(path)
        new_render_component = RenderComponent(sprite)
        new_position_component = PositionComponent(x,y,sprite.get_rect())
        new_physics_component = PhysicsComponent(shape)

        self.entity_manager.addComponent(new_entity, new_position_component)
        self.entity_manager.addComponent(new_entity, new_render_component)
        self.entity_manager.addComponent(new_entity, new_physics_component)
        self.entity_manager.addComponent(new_entity, new_path_component)

        self.group_manager.add(new_entity, 'moving_platform')
        self.group_manager.add(new_entity, 'dynamic_obstructor')
        return new_entity
