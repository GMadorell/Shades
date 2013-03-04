import larv


class StateComponent(larv.Component):
    """
    Entities that must support states (state machines) need to have this
    component.
    A good example of that can be the hero, that has death state, jump state,
    idle state, etc.
    Useful when animating.
    """
    def __init__(self, initial_state):
        self.state = initial_state

        self.initial_state = initial_state # useful for returning level to original position