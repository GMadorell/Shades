import larv

class LevelInfoComponent(larv.Component):
    """
    Holds information about things relative to the level,
    such as:
        - Camera limit variables.
        - Player start and finish point (in standarized coordinates).
    """
    def __init__(self):
        self.camera_x_limit_right = 0
        self.camera_x_limit_left = 0
        self.camera_y_limit_top = 0
        self.camera_y_limit_bottom = 0

        self.player_start = (0, 0)
        self.player_finish = (0, 0)

        self.debug = False

        self.level_name = None # holds level name

        self.initial_state = None # holds the initial info about the game