import larv
import pygame

from Pieces.Components import *
from ColorConstants import *


class MenuEntityFactory(larv.EntityFactory):
    def createText(self, x, y, text, function, args, active_color=RED,
                   inactive_color=WHITE, type='freesansbold.ttf', size=16):
        new_entity = self.entity_manager.createEntity()

        font_obj = pygame.font.Font(type, size) 
        active_surface = font_obj.render(text, True, active_color) # string, antialising, letter color, bg color
        rect = active_surface.get_rect()
        inactive_surface = font_obj.render(text, True, inactive_color)

        new_position_component = PositionComponent(x, y, rect)
        new_render_component = RenderComponent(inactive_surface)
        new_state_component = StateComponent('inactive')
        new_menu_button_component = MenuButtonComponent(active_surface, inactive_surface)
        new_on_press_component = OnPressComponent(function, args)

        self.entity_manager.addComponent(new_entity, new_position_component)
        self.entity_manager.addComponent(new_entity, new_render_component)
        self.entity_manager.addComponent(new_entity, new_state_component)
        self.entity_manager.addComponent(new_entity, new_menu_button_component)
        self.entity_manager.addComponent(new_entity, new_on_press_component)

        self.group_manager.add(new_entity, 'text')
        return new_entity

    def createRenderObject(self, sprite, x, y):
        rect = sprite.get_rect()

        new_entity = self.entity_manager.createEntity()

        new_position_component = PositionComponent(x, y, rect)
        new_render_component = RenderComponent(sprite)

        self.entity_manager.addComponent(new_entity, new_position_component)
        self.entity_manager.addComponent(new_entity, new_render_component)

        return new_entity