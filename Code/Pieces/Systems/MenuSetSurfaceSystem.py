import larv

from ..Components import MenuButtonComponent
from ..Components import RenderComponent
from ..Components import StateComponent

class MenuSetSurfaceSystem(larv.System):
    """
    Sets the surface of the menu elements that can change depending on their
    state to the correct one.
    """
    def update(self):
        # Get the entities
        list_entities = self.entity_manager.getEntitiesHavingComponents(
                                                MenuButtonComponent.__name__,
                                                RenderComponent.__name__,
                                                StateComponent.__name__
                                            )
        # Iterate over them
        for entity in list_entities:
            menu_button_comp = self.entity_manager.getComponent(entity, MenuButtonComponent.__name__)
            render_comp = self.entity_manager.getComponent(entity, RenderComponent.__name__)
            state_comp = self.entity_manager.getComponent(entity, StateComponent.__name__)

            if state_comp.state == 'active':
                render_comp.sprite = menu_button_comp.active_surface
            elif state_comp.state == 'inactive':
                render_comp.sprite = menu_button_comp.inactive_surface