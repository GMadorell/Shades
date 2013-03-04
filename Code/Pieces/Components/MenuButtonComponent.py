import larv

class MenuButtonComponent(larv.Component):
    """
    Component that has 2 surfaces, one for when the button isn't currently
    activated and one for when the button is active.
    To be used with other components such as StateComponent.
    """
    def __init__(self, active_surface, inactive_surface):
        self.active_surface = active_surface
        self.inactive_surface = inactive_surface