# -*- coding: UTF-8 -*-
import pymunkoptions
pymunkoptions.options['debug'] = False

import pymunk
import pygame
import larv

from pygame.locals import *

print('globals')

# Initiate pygame
pygame.init()

# Initiate larv
WORLD = larv.World()

WIN_WIDTH = 1280
WIN_HEIGHT = 720
DISPLAYSURF = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Shades")

FPS = 60
FPS_CLOCK = pygame.time.Clock()

# File used for saving Shades advance
SAVE_FILE = 'Shades_save_file.dat'

# DEBUG_MODE = False
DEBUG_MODE = True

### MOVEMENT
MAX_X_VELOCITY = 400    # Max velocity the hero can move horizontally
X_ACCELERATION = 30     # Amount per frame the hero speed changes when moving
MAX_JUMP_SPEED = 400    # Max speed the hero will be allowed when jumping
# MAX_JUMP_SPEED = 1000
JUMP_ACCELERATION = 40  # Amount per frame the hero speed will increase when pressing jump
## Laser
LASER_MAX_VELOCITY = 300
LASER_ACCELERATION = 300
PERMANENT_LASER_INTERVAL = 15
## Platforms
MOVING_PLATFORM_SPEED = 2

### CHIPMUNK
GRAVITY = (0, -700)
SPACE = pymunk.Space()
SPACE.gravity = GRAVITY
STD_FRICTION = 0.8
HERO_FRICTION = 1.0

### LIGHT
DEFAULT_LIGHT_ALPHA = 100

### COLLISION TYPES
HERO_C_TYPE = 1
COLLISION_C_TYPE = 2
ENEMY_C_TYPE = 3
MOVABLE_C_TYPE = 4
SHOT_C_TYPE = 5
MOVING_PLATFORM_C_TYPE = 6

### GROUPS - Chipmunk
LASER_GROUP = 1
REMOVE_GROUP = 666 # special group, used for knowing when to delete that physics object 


### SOUNDS
MENU_MUSIC = 'Images\\Sounds\\Home Base Groove.ogg'
SNOW_QUEEN_MUSIC = 'Images\\Sounds\\The Snow Queen.ogg'
SPACE_FIGHTER_MUSIC = 'Images\\Sounds\\Space Fighter Loop.ogg'
JUMP_SOUND = pygame.mixer.Sound('Images\\Sounds\\jump.wav')
JUMP_SOUND.set_volume(0.15)
LAND_SOUND = pygame.mixer.Sound('Images\\Sounds\\land.wav')
# JUMP_SOUND.set_volume(2)
LASER_SOUND = pygame.mixer.Sound('Images\\Sounds\\laser.wav')
LASER_SOUND.set_volume(0.1)
#Music map
# MUSIC_MAP = { 'level1' : SNOW_QUEEN_MUSIC,
#               'level2' : SNOW_QUEEN_MUSIC,
#               'level3' : SNOW_QUEEN_MUSIC,
#               'level4' : SNOW_QUEEN_MUSIC,
#               'level5' : SNOW_QUEEN_MUSIC,
#               'level6' : SPACE_FIGHTER_MUSIC,
#               'level7' : SPACE_FIGHTER_MUSIC,
#               'level8' : SPACE_FIGHTER_MUSIC,
#               'level9' : SPACE_FIGHTER_MUSIC,
#               'level10': SPACE_FIGHTER_MUSIC}
