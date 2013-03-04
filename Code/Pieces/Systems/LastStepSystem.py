import larv

from Globals import *

class LastStepSystem(larv.System):
    """
    Does the last steps of the game loop:
      - Updates physics engine (if physics bool is True)
      - Updates pygame display
      - Sets the frame clock correctly
    """
    def __init__(self, physics = True):
        self.physics = physics

    def update(self):
        # Update the physics engine
        if self.physics:
            SPACE.step(1/FPS)
        # Update the window (paint everything)
        pygame.display.flip()
        # Wait so FPS get accomplished
        FPS_CLOCK.tick(FPS)