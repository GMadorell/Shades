import larv
import time

from ..Components import IntermitentComponent
from ..Components import StateComponent

class IntermitentSystem(larv.System):
    """
    Processes those entities that have an intermitent component.
    Those entities are required to have also an state component, which the 
    system puts on active status.
    """
    def update(self):
        # We get the entities that have intermitent and state components.
        entity_list = self.entity_manager.getEntitiesHavingComponents(
                            IntermitentComponent.__name__,
                            StateComponent.__name__
                        )

        for entity in entity_list:
            # print('IntermitentSystem inside entity loop')
            intermitent_comp = self.entity_manager.getComponent(entity, IntermitentComponent.__name__)
            state_comp = self.entity_manager.getComponent(entity, StateComponent.__name__)

            # If the time wasn't inicialized, we do so and continue with the next entity
            if intermitent_comp.time is None:
                intermitent_comp.time = time.time()
                continue

            # We get the time difference in milliseconds
            time_passed = (time.time() - intermitent_comp.time)*1000

            if time_passed > intermitent_comp.interval:
                # Switch the state
                if state_comp.state == 'active':
                    state_comp.state = 'inactive'
                else:
                    state_comp.state = 'active'

                # Set timer to actual time
                intermitent_comp.time = time.time()

