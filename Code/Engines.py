import Pieces
import larv
import PymunkCollisions
import XMLParser
import pymunk
import helper

from Globals import *

class LevelEngine:
    """
    Supports a playable level loaded from a xml file.
    """
    def __init__(self, filename):
        # Initialize the framework
        self.entity_factory = Pieces.LevelEntityFactory()
        self.engine = larv.Engine(self.entity_factory)

        # Reset physics world
        SPACE.__init__()
        SPACE.gravity = GRAVITY
        # Enable custom collisions
        PymunkCollisions.createCollisions(self.engine)

        # Parse given level
        parser = XMLParser.XMLParser()
        parser.importXML(filename)
        parser.initiateLevel(self.entity_factory)

        # Create entities
        self.entity_factory.createCamera()

        # TODO, add a milion ifs to check if components exist in the level and
        # then add systems dinamically depending on those components
        # (only add certain systems if the requirements are met, the most 
        #  obvious example being that the IntermitentSystem shouldn't be created
        #  if no intermitent lights (intermitent components) exist)
        em = self.engine.entity_manager
        gm = self.engine.group_manager

        ### Create systems dinamically (this needs to be revised when system
        ### requirements get changed!!)

        # Get info on what groups does the level have
        # has__group = gm.doesGroupExist('')
        has_hero_group = gm.doesGroupExist('hero')
        has_camera_group = gm.doesGroupExist('camera')
        has_level_info_group = gm.doesGroupExist('level_info')

        # Get bools about components that the current level has
        has_intermitent_comp = Pieces.IntermitentComponent.__name__ in em.componentsByClass
        has_level_info_comp = Pieces.LevelInfoComponent.__name__ in em.componentsByClass
        has_light_comp = Pieces.LightComponent.__name__ in em.componentsByClass
        has_move_comp = Pieces.MoveComponent.__name__ in em.componentsByClass
        has_on_press_comp = Pieces.OnPressComponent.__name__ in em.componentsByClass
        has_physics_comp = Pieces.PhysicsComponent.__name__ in em.componentsByClass
        has_position_comp = Pieces.PositionComponent.__name__ in em.componentsByClass
        has_render_comp = Pieces.RenderComponent.__name__ in em.componentsByClass
        has_state_comp = Pieces.StateComponent.__name__ in em.componentsByClass

        # Depending on which components we have, select which systems need to be
        # created.
        systems = []
        if has_camera_group and has_hero_group and has_level_info_group and\
            has_level_info_comp and has_position_comp:
            systems.append((Pieces.CameraSystem(), 3))

        if has_hero_group and has_position_comp and has_state_comp and has_level_info_comp:
            systems.append((Pieces.GameManagerSystem(), 0))

        if has_level_info_comp and has_position_comp and has_physics_comp\
            and has_state_comp and has_hero_group:
            systems.append((Pieces.HeroStateSystem(), 19))

        if has_intermitent_comp and has_state_comp:
            systems.append((Pieces.IntermitentSystem(), 1))

        systems.append((Pieces.LastStepSystem(), 100)) #always needs to be there

        if has_hero_group and has_move_comp and has_physics_comp\
            and has_level_info_comp:
            systems.append((Pieces.LevelInputSystem(), 4))

        if has_light_comp and has_position_comp and has_level_info_comp \
            and has_state_comp and has_camera_group and has_hero_group:
            systems.append((Pieces.LightSystem(), 17))

        if has_physics_comp and has_move_comp:
            systems.append((Pieces.MoveSystem(), 5))

        if has_physics_comp and has_position_comp:
            systems.append((Pieces.PositionSystem(), 6))

        if has_position_comp and has_render_comp:
            systems.append((Pieces.RenderSystem(), 20))

        systems.append((Pieces.ItemManagerSystem(), 0)) 

        # # Add systems to the engine
        # self.engine.addSystem(game_manager_system, 0)
        # self.engine.addSystem(intermitent_system, 1)
        # self.engine.addSystem(camera_system, 3)
        # self.engine.addSystem(input_system, 4)
        # self.engine.addSystem(move_system, 5)
        # self.engine.addSystem(position_system, 6)
        # self.engine.addSystem(light_system, 17)
        # self.engine.addSystem(hero_state_system, 19)
        # self.engine.addSystem(render_system, 20) # priority, less is before
        # self.engine.addSystem(last_step_system, 100)

        # Add all the systems to the engine using the priority inserted before
        for system in systems:
            # print(system[0])
            self.engine.addSystem(system[0], system[1])

class MainMenuEngine:
    """
    Supports creating a menu.
    """
    def __init__(self):
        self.entity_factory = Pieces.MenuEntityFactory()
        self.engine = larv.Engine(self.entity_factory)

        # Position variables (0,0 is botleft)
        start_x = WIN_WIDTH//2
        start_y = WIN_HEIGHT - 250

        exit_x = WIN_WIDTH//2
        exit_y = WIN_HEIGHT - 350

        # Create entities
        # Background
        img = pygame.image.load('Images\\menu_screen.png')
        self.entity_factory.createRenderObject(img, WIN_WIDTH//2, WIN_HEIGHT//2)

        # Button information        
        button_img = pygame.image.load('Images\\button.png')
        font_type = 'Images\\Fonts\\Dimbo regular.ttf'
        font_size = 36
        # Create start button
        def start():
            WORLD.push(LevelMenuEngine().engine)
        function = start
        self.entity_factory.createRenderObject(button_img, start_x, start_y)
        self.entity_factory.createText(start_x, start_y, 'START', function=function, args=[],
                                       type=font_type, size=font_size)
        
        def raiseEndException():
            raise larv.EndProgramException()        
        self.entity_factory.createRenderObject(button_img, exit_x, exit_y)
        self.entity_factory.createText(exit_x, exit_y, 'END GAME', function=raiseEndException, args=[],
                                       type=font_type, size=font_size)

        # Create systems
        menu_manager_system = Pieces.MenuManagerSystem()
        render_system = Pieces.RenderSystem()
        last_step_system = Pieces.LastStepSystem(physics=False)
        menu_set_surface_system = Pieces.MenuSetSurfaceSystem()
        menu_input_system = Pieces.MenuInputSystem()

        # Add systems to the engine
        self.engine.addSystem(menu_manager_system, 0)
        self.engine.addSystem(menu_input_system, 5)
        self.engine.addSystem(menu_set_surface_system, 15)
        self.engine.addSystem(render_system, 20)
        self.engine.addSystem(last_step_system, 100)

class LevelMenuEngine:
    """
    Supports creating a menu.
    """
    def __init__(self):
        self.entity_factory = Pieces.MenuEntityFactory()
        self.engine = larv.Engine(self.entity_factory)

        ### Create entities
        # Load background of the buttons
        img = pygame.image.load('Images\\level_button.png')
        # Letter info
        font = 'Images\\Fonts\\Dimbo Regular.ttf'
        size = 24
        # Set information of the position of the buttons (5 buttons per line)
        # This is only for easier configuration
        separation = img.get_width()*2
        y_first_line  = WIN_HEIGHT - 100 
        y_second_line = WIN_HEIGHT - 200
        y_third_line  = WIN_HEIGHT - 300
        y_back_button = 100

        l1_x = WIN_WIDTH//2 - separation*2
        l1_y = y_first_line 

        l2_x = WIN_WIDTH//2 - separation
        l2_y = y_first_line

        l3_x = WIN_WIDTH//2
        l3_y = y_first_line

        l4_x = WIN_WIDTH//2 + separation
        l4_y = y_first_line

        l5_x = WIN_WIDTH//2 + separation*2
        l5_y = y_first_line
        #------------------
        l6_x = WIN_WIDTH//2 - separation*2
        l6_y = y_second_line

        l7_x = WIN_WIDTH//2 - separation
        l7_y = y_second_line

        l8_x = WIN_WIDTH//2
        l8_y = y_second_line

        l9_x = WIN_WIDTH//2 + separation
        l9_y = y_second_line

        l10_x = WIN_WIDTH//2 + separation*2
        l10_y = y_second_line
        #-----------------
        l11_x = WIN_WIDTH//2 - separation*2
        l11_y = y_third_line

        l12_x = 0
        l12_y = 0

        #-----------------
        go_back_x = WIN_WIDTH//2
        go_back_y = y_back_button

        # Add all the info we have got into a list for easier creation of the
        # buttons.
        buttons_position = [(l1_x, l1_y), (l2_x, l2_y), (l3_x, l3_y), (l4_x, l4_y),
                           (l5_x, l5_y), (l6_x, l6_y), (l7_x, l7_y), (l8_x, l8_y),
                           (l9_x, l9_y), (l10_x, l10_y)]
        # Append the back button
        buttons_position.append((go_back_x, go_back_y))

        # Create the background of the buttons, the button image
        for position in buttons_position:
            x, y = position[0], position[1]
            self.entity_factory.createRenderObject(img, x, y)

        # Create the texts of the level buttons, which link to the functions
        # to load the levels.
        def loadLevelN(level):
            """
            Checks if that level is avaiable to play (the level before it has
            been complete). If that holds True allows to play it.
            Doesn't work for level one.
            @level: of the form 'level1'
            """
            # Level1 is an exception, should be always loaded
            if level == 'level1':
                level = 'levels\\' + level + '.xml'
                WORLD.push(LevelEngine(level).engine)
                # pygame.mixer.music.stop()
                return

            save_file = helper.getSaveFile()
            # Separate letters from numbers
            level_before = ''
            digits = ''
            for char in level:
                if char.isdigit():
                    digits += str(int(char))
                else:
                    level_before += char
            # Substract 1
            digits = str(int(digits)-1)
            # Form the level before
            level_before += digits

            # If the previous level was complete, we allow to load it
            if save_file[level_before]['complete']:
                level = 'levels\\' + level + '.xml'
                WORLD.push(LevelEngine(level).engine)
                # pygame.mixer.music.stop()
            else: #we don't allow it
                print('Can\'t be allowed')

        for n, position in enumerate(buttons_position[:-1], start=1):
            x, y = position[0], position[1]
            level = 'level' + str(n)
            self.entity_factory.createText(x,y, str(n), function=loadLevelN,
                                           args=[level], size=size, type=font)

        # Create the go back text
        def goBack():
            WORLD.pop()
        self.entity_factory.createText(go_back_x, go_back_y, 'BACK',
                                       function=goBack, args=[], size=size,
                                       type=font)

        # Create systems
        menu_manager_system = Pieces.MenuManagerSystem()
        render_system = Pieces.RenderSystem()
        last_step_system = Pieces.LastStepSystem(physics=False)
        menu_set_surface_system = Pieces.MenuSetSurfaceSystem()
        menu_input_system = Pieces.MenuInputSystem()

        # Add systems
        self.engine.addSystem(menu_manager_system, 0)
        self.engine.addSystem(menu_input_system, 5)
        self.engine.addSystem(menu_set_surface_system, 15)
        self.engine.addSystem(render_system, 20)
        self.engine.addSystem(last_step_system, 100)

class StartMenuEngine:
    """
    Supports creating a menu.
    """
    def __init__(self):

        self.entity_factory = Pieces.MenuEntityFactory()
        self.engine = larv.Engine(self.entity_factory)

        img = pygame.image.load('Images\\start_screen.png')
        self.entity_factory.createRenderObject(img,WIN_WIDTH//2,WIN_HEIGHT//2)

        render_system = Pieces.RenderSystem()
        last_step_system = Pieces.LastStepSystem(physics=False)
        menu_input_system = Pieces.StartMenuInputSystem()

        self.engine.addSystem(menu_input_system, 5)
        self.engine.addSystem(render_system, 10)
        self.engine.addSystem(last_step_system, 15)