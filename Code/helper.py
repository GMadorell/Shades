# -*- coding: UTF-8 -*-
import pygame
from pygame.constants import *
import pymunk
from pymunk.vec2d import Vec2d
import copy
from ColorConstants import *
import math
# from comparable import Comparable
import sys
import os
import pickle

from Globals import *

def terminate():
    """Ends the game and closes everything."""
    pygame.quit()
    sys.exit() 

def toPygame(vector):
    """
    Little hack to pass a pymunk's vec2d vector to a (x, y) tuple usable in
    pygame coordinates.
    @p: instance of pymunk.vec2d.Vec2d
    """
    return int(vector.x), int(WIN_HEIGHT - vector.y)

def xyToPygame(x, y):
    """Translates real coordinates into pygame."""
    return int(x), int(WIN_HEIGHT - y)

def toPymunk(*args):
    """
    Little hack to pass pygame coordinates to a pymunk's vec2d.
    One can give x, y as different variables or just a (x, y) tuple.
    Modes of usage:
        toPymunk(x, y)
        toPymunk(tuple_xy)
    """
    if len(args) == 1:
        return pymunk.vec2d.Vec2d(args[0][0], WIN_HEIGHT - args[0][1])
    else:
        return pymunk.vec2d.Vec2d(args[0], WIN_HEIGHT - args[1])

def createShapeBodyFromImage(surface, mass = 0, x = None, y = None, mode = 'static',
                             rotable = True, centered = True):
    """
    Create a pymunk object (body + polygonal shape) from a surface.
    The shape we add to the sprite will be a rectangle.
    Requires a global variable for pymunk's SPACE (SPACE.add).
    @surface: surface obtained from pygame.image.load
    @mass: mass of the object (gravity, moment, etc)
    @x, y: initial position (top left) of the body, may not be passed, coordinates in
           real value (pymunk value).
    @mode: dynamic/static (will move/will not move).
    @rotable: only usable if mode is dynamic. Set's inertia to infinite so body can't rotate.
              Warning: if 2 unrotable (rotable = False) bodies connect, world may explode.
              Useful for the hero object, so he doesn't bounce from platforms.
    @centered: bool, if True, position will be set at the gravity point (middle)
               of the sprite. If false, position set at top left.
    """
    mode = mode.lower()
    assert mode in ('dynamic', 'static')

    height = surface.get_height()
    width = surface.get_width()
    top_left =     (-width//2, -height//2)
    top_right =    ( width//2, -height//2)
    bottom_left =  (-width//2,  height//2)
    bottom_right = ( width//2,  height//2)
    vertices = (top_left, top_right, bottom_right, bottom_left)

    if mode == 'static':
        body = pymunk.Body()
    else: # dynamic
        if rotable:
            inertia = pymunk.moment_for_poly(mass, vertices)
        else: # not rotable
            inertia = pymunk.inf
        body = pymunk.Body(mass, inertia)

    if x is not None and y is not None:
        if centered:
            body.position = (x, y) # 
        else:
            body.position = (x + width//2, y - height//2)
    shape = pymunk.Poly(body, vertices)
    if mode == 'static':
        SPACE.add(shape)
    else: # dynamic
        SPACE.add(body, shape)
    return shape

def createCollision(x, y, width, height):
    """
    Helper function to help create collision from the given data.
    Creates a polygonal shape into a static body and returns the shape.
    @x,y: coordinates standarized of top_left point
    @width, height: pretty obvious
    """
    top_left =     (-width//2, -height//2)
    top_right =    ( width//2, -height//2)
    bottom_left =  (-width//2,  height//2)
    bottom_right = ( width//2,  height//2)
    vertices = (top_left, top_right, bottom_right, bottom_left)

    # create static body
    body = pymunk.Body()
    body.position = (x + width//2, y - height//2)
    shape = pymunk.Poly(body, vertices)

    SPACE.add(shape)
    return shape

def outputText(text, x, y, color = BLACK, size = 16, centered = False, surface=DISPLAYSURF):
    """
    Outputs given text string to the given x, y coordinates.
    Can also change color and size of the text.
    If centered is True, text will be centered around x and y given coordinates.
    """
    fontObj = pygame.font.Font('freesansbold.ttf', size) 
    textSurface = fontObj.render(text, True, color) # string, antialising, letter color, bg color
    textRect = textSurface.get_rect()
    if centered:
        textRect.center = (x, y)
    else:
        textRect.topleft = (x, y)
    surface.blit(textSurface, textRect)


#### SAVE FILE MANAGEMENT - uses Pickle atm - could be improved to binary mode for safety
def createSaveFile():
    """
    Creates the save file, if and only if it didn't exist before.
    """
    dic = {'level1':  {'complete': True},
           'level2':  {'complete': True},
           'level3':  {'complete': True},
           'level4':  {'complete': True},
           'level5':  {'complete': True},
           'level6':  {'complete': True},
           'level7':  {'complete': True},
           'level8':  {'complete': True},
           'level9':  {'complete': True},
           'level10': {'complete': True}}
           
    if not os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'w+b') as fd:            
            pickle.dump(dic, fd, pickle.HIGHEST_PROTOCOL)

def getSaveFile():
    """
    Returns the dict object stored in the save file.
    """
    assert os.path.exists(SAVE_FILE)
    with open(SAVE_FILE, 'r+b') as fd: 
        return pickle.load(fd)

def deleteSaveFile():
    """
    If the save file exists, deletes it from the disk.
    """
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)

def modifySaveFile(content):
    """
    If the save file exists, substitutes it's actual content for the given content.
    @content: must be pickable
    """
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'w+b') as fd:
            pickle.dump(content, fd, pickle.HIGHEST_PROTOCOL)
