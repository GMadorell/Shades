# -*- coding: UTF-8 -*-
"""
The purpose of this file is to modify pymunk's SPACE:
  - Add diferent collision handlers
"""

import pymunk
import math

from Globals import *
from ColorConstants import *

import Pieces


def createCollisions(engine = None):
    """
    Creates different collisions depending on the type of the entities that
    collide.
    """
    global COLLISION_ENGINE
    COLLISION_ENGINE = engine
    # When Hero touches any enemy type entity, or a shot, set status to die
    SPACE.add_collision_handler(HERO_C_TYPE, ENEMY_C_TYPE, pre_solve=heroContactEnemy)
    SPACE.add_collision_handler(HERO_C_TYPE, SHOT_C_TYPE, pre_solve=heroContactEnemy)

    # When a shot collides with any collision, remove it
    # SPACE.add_collision_handler(SHOT_C_TYPE, HERO_C_TYPE, post_solve=removeFirst)
    SPACE.add_collision_handler(SHOT_C_TYPE, COLLISION_C_TYPE, pre_solve=removeFirst)
    SPACE.add_collision_handler(SHOT_C_TYPE, ENEMY_C_TYPE, pre_solve=removeFirst)
    SPACE.add_collision_handler(SHOT_C_TYPE, MOVING_PLATFORM_C_TYPE, pre_solve=removeFirst)

    # When hero is on a moving platform
    SPACE.add_collision_handler(HERO_C_TYPE, MOVING_PLATFORM_C_TYPE, post_solve=itemContactMovingPlatform)



def heroContactEnemy(space, arbiter):
    """
    Create a new collision definition, when the hero touches a enemy,
    reset hero's position (die).
    """
    hero_shape = arbiter.shapes[0]
    def returnToOrigin(obj):
        # get group manager and entity manager
        gm = COLLISION_ENGINE.group_manager
        em = COLLISION_ENGINE.entity_manager

        # get hero enitty and change his state to dead
        hero = gm.get('hero')[0]        
        state_comp = em.getComponent(hero, Pieces.StateComponent.__name__)
        state_comp.state = 'dead'
    
    # the function will be done after the next physics step    
    SPACE.add_post_step_callback(returnToOrigin, hero_shape)
    return False

def removeFirst(space, arbiter):
    """
    Removes completely the first element of the collision.
    In a system, must check for every physics component if they meet the 
    requirement of pertaining to the remove group -> delete them.
    """
    first_shape = arbiter.shapes[0]
    def delete(first_shape):
        body = first_shape.body
        # first_shape.body = None
        first_shape.group = REMOVE_GROUP
        SPACE.remove(first_shape, body)
    SPACE.add_post_step_callback(delete, first_shape)
    return False

def itemContactMovingPlatform(space, arbiter):
    """
    Adjust the position of the first shape (which is considered the item) according
    to the velocity of the moving platform (considered to be the second shape).
    That causes that the item moves according to the platform.
    """
    item = arbiter.shapes[0]
    platform = arbiter.shapes[1]
    if item.body.position.y > platform.body.position.y:
        platform_velocity = platform.body.velocity
        item.body.position += platform_velocity * FPS
    else: #collide
        # Search for the item affected by collision
        # If it has a move component, don't allow it to move anymore upside
        # This was done to fix a bug that happened when the hero jumped directly
        # to the bottom of a platform that was very near to the floor.
        # When that happened, the hero got stuck into the platform until the player
        # released the jumping button.
        em = COLLISION_ENGINE.entity_manager
        list_entities = em.getEntitiesHavingComponent(Pieces.PhysicsComponent.__name__)
        for entity in list_entities:
            physics_comp = em.getComponent(entity, Pieces.PhysicsComponent.__name__)
            body = physics_comp.shape.body
            if body == item.body:
                # Found entity
                if not em.hasComponent(entity, Pieces.MoveComponent.__name__):
                    break
                move_comp = em.getComponent(entity, Pieces.MoveComponent.__name__)
                move_comp.move_up = False
    return True