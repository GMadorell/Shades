# -*- coding: UTF-8 -*-
import pygame
import larv
import helper
import Engines

from ..Components import MoveComponent
from ..Components import PhysicsComponent
from ..Components import LevelInfoComponent

from ..Systems import RenderSystem

from pygame.constants import *
from ColorConstants import *
from Globals import *

class LevelInputSystem(larv.System):
    """
    Takes the hero entity and updates it using the input.
    """
    def update(self):
        hero = self.group_manager.get('hero')[0]
        move_comp = self.entity_manager.getComponent(hero, MoveComponent.__name__)
        physics_comp = self.entity_manager.getComponent(hero, PhysicsComponent.__name__)

        #### JUST FOR DEBUGGING PURPOSES
        level_info = self.group_manager.get('level_info')[0]
        level_info_comp = self.entity_manager.getComponent(level_info, LevelInfoComponent.__name__)
        ####

        for event in pygame.event.get():
            if event.type == QUIT:
                helper.terminate()

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    # WORLD.pop()
                    self.pause()

                if event.key == K_RIGHT:
                    move_comp.move_right = True
                    move_comp.move_left = False

                if event.key == K_LEFT:
                    move_comp.move_right = False
                    move_comp.move_left = True

                if event.key == K_UP:
                    if not move_comp.mid_air:
                        # physics_comp.shape.body.velocity.y = JUMP_SPEED
                        move_comp.move_up = True
                        # Jump sound
                        JUMP_SOUND.play()

            elif event.type == KEYUP:
                if event.key == K_RIGHT:
                    move_comp.move_right = False

                if event.key == K_LEFT:
                    move_comp.move_left = False

                if event.key == K_UP:
                    move_comp.move_up = False



                #####
                #####
                ## DEBUG THINGS
                if event.key == K_o:                   
                    if level_info_comp.debug == True:
                        level_info_comp.debug = False
                    else:
                        level_info_comp.debug = True

    def pause(self):        
        # Huge hack done here to render the screen and then copy it.
        # This allows us to have a 'screenshoot' of the actual game state for
        # displaying the pause creen on top of that.
        render_system = RenderSystem()
        render_system.bindToEntityManager(self.entity_manager)
        render_system.bindToGroupManager(self.group_manager)
        render_system.update()
        render_system = None
        
        freezed_surface = DISPLAYSURF.copy()

        # Load images
        dark_img = pygame.image.load('Images\\dark.png')

        # Lower the sound
        pygame.mixer.music.set_volume(0.4)

        # Initialise variables
        paused = True
        caught_events = list()
        i = 0
        while paused:
            # Copy the surface to modify it
            copied_surface = freezed_surface.copy()

            # Darken the image
            copied_surface.blit(dark_img, (0,0))

            # Output text
            helper.outputText('PAUSE', WIN_WIDTH//2, WIN_HEIGHT//2, centered=True,
                              size = 200, surface = copied_surface)

            helper.outputText('Press Q to return to level screen', WIN_WIDTH//2, WIN_HEIGHT//2+150,
                               centered=True, size = 50, surface = copied_surface)

            helper.outputText('Press ESC to resume the game', WIN_WIDTH//2, WIN_HEIGHT//2+215,
                               centered=True, size = 50, surface = copied_surface)
 
            # Process events
            for event in pygame.event.get():
                if event.type == QUIT:
                    helper.terminate()

                elif event.type == KEYDOWN:
                    # If we press escape, return to the level to play it
                    if event.key == K_ESCAPE:
                        paused = False
                    elif event.key == K_q:
                        WORLD.change(Engines.LevelMenuEngine().engine)
                        paused = False

                # Add the keyup events onto the caught events list to add them
                # later to the stack. This avoids free running after pause.
                elif event.type == KEYUP:
                    if event not in caught_events:
                        caught_events.append(event)

            # Finally, we blit the copied surface into the original surface
            DISPLAYSURF.blit(copied_surface, (0,0))
            FPS_CLOCK.tick()
            pygame.display.update()

        # Readd the caught events onto the event stack
        for event in caught_events:
            pygame.event.post(event)

        # Increase sound volume
        pygame.mixer.music.set_volume(0.8)
