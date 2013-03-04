import larv

class MoveComponent(larv.Component):
    """
    Holds info about a pymunk's shape and body structure.
    """
    def __init__(self, move_right = False, move_left = False, move_up = False, mid_air = True,
                 move_down = False, max_x_velocity = None, x_acceleration = None,
                 max_y_speed = None, y_acceleration = None):

        self.move_right = move_right
        self.move_left = move_left
        self.move_up = move_up
        self.move_down = move_down
        self.mid_air = mid_air

        self.max_x_velocity = max_x_velocity
        self.x_acceleration = x_acceleration
        self.max_y_speed = max_y_speed
        self.y_acceleration = y_acceleration