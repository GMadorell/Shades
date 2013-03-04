# -*- coding: UTF-8 -*-
import xml
import xml.parsers.expat
import xml.dom.minidom

import os
import sys
import pprint
import larv
import pygame

from Globals import *

class XMLParser:
    """
    Provides a way to load maps done in Gleed2D map editor.
    Stores the data in a dictionary of dictionaries of dictionaries.
    The first value represents the layer, the second one the objects
    of that layer and the third one the attributes of that object, such as
    position.

    Also has a helper method to populate the map (create entities) from a given
    entity_factory and the data parsed from the xml file.

    Level structure supported:
    - layers:
      - background: first layer to be rendered, just images
      - terrain: second layer to be rendered, contains terrain and all things that
                 are just rendered, they do nothing but to exist and be painted.
      - collision: contains logic rectangles (don't render them) only.
                   This rectangles define those parts of the map the player should
                   collide with (floor, platforms).
      - items:
            - crates, sprites, must have crate in name
            - intermitent lasers: must have intermitent and laser in name
                - direction: up, down, right, left (text)
                - interval: miliseconds (Vec2d)
            - permanent lasers: must have permanent and laser in name
                - direction: up, down, right, left (text)
            - moving platforms: must have moving and platform in name
                - must be a path
                - with a sprite text property used containing path to img (named sprite)

      - logic: random logic of the game goes here, such as:
            - player_start: circle logic
            - player_finish: circle logic
            - camera_x_limit_right, camera_x_limit_left, camera_y_limit_top, camera_y_limit_bottom
            - level_name: circle logic with text propery called 'level_name' with the name of the level without .xml at the end
      - death:
            - static enemies
            - death zones
      - light:
            - lights (circle logic with size custom property (vec2d with value in x))
            - obstructors (rectangles)
            - intermitent lights, must have:
                - intermitent in name
                - interval (in milliseconds)(vec2d)
                - size (vec2d)
    """
    def __init__(self):
        self.data = {}

    def importXML(self, filename):
        """
        Reads the given file and fills self.data with file's information.
        Returns True if success, False if failed to parse.
        @filename: path to the file so it can be opened.
        """
        ## Helper function to parse attributes
        def get_text(node_list):
            text = []
            for node in node_list:
                if node.nodeType == node.TEXT_NODE:
                    text.append(node.data)
            return ''.join(text).strip()

        try:
            dom = xml.dom.minidom.parse(filename)
        except (EnvironmentError, xml.parsers.expat.ExpatError) as err:
            print('{0}: import error: {1}'.format(os.path.basename(sys.argv[0]), err))
            return False

        self.data = {}
        for layer in dom.getElementsByTagName('Layer'):
            layer_name = layer.getAttribute('Name')
            items = {}
            for item in layer.getElementsByTagName('Item'):
                item_name = item.getAttribute('Name')
                attributes = {}
                # parse the position 
                for attribute in item.getElementsByTagName('Position'):
                    x = attribute.getElementsByTagName('X')[0]
                    x_value = int(get_text(x.childNodes))
                    y = attribute.getElementsByTagName('Y')[0]
                    y_value = int(get_text(y.childNodes)) * -1 # so it gets positive
                    attributes['x'] = x_value
                    attributes['y'] = y_value

                # parse the sprite attached to it
                attribute = item.getElementsByTagName('texture_filename')
                # not every item has a sprite, so we must discard those who don't
                if attribute: 
                    sprite = get_text(attribute[0].childNodes)
                    attributes['sprite'] = sprite

                # parse the possible width and height attributes (for collision)
                attribute = item.getElementsByTagName('Width')
                if attribute: 
                    width = int(get_text(attribute[0].childNodes))
                    attributes['width'] = width
                attribute = item.getElementsByTagName('Height')
                if attribute: 
                    height = int(get_text(attribute[0].childNodes))
                    attributes['height'] = height

                # Parse Custom Properties
                for properties in item.getElementsByTagName('CustomProperties'):
                    # See the name of the property
                    for custom_property in properties.getElementsByTagName('Property'):
                        property_name = custom_property.getAttribute('Name')
                        # Switch every property for custom cases
                        if property_name == 'size':
                            for vector2 in custom_property.getElementsByTagName('Vector2'):
                                size = vector2.getElementsByTagName('X')[0]
                                size_value = int(get_text(size.childNodes))
                                attributes['size'] = size_value
                        elif property_name == 'alpha':
                            for vector2 in custom_property.getElementsByTagName('Vector2'):
                                alpha = vector2.getElementsByTagName('X')[0]
                                alpha_value = int(get_text(alpha.childNodes))
                                attributes['alpha'] = alpha_value
                        elif property_name == 'interval':
                            for vector2 in custom_property.getElementsByTagName('Vector2'):
                                interval = vector2.getElementsByTagName('X')[0]
                                interval_value = int(get_text(interval.childNodes))
                                attributes['interval'] = interval_value
                        elif property_name == 'level_name':
                            attribute = custom_property.getElementsByTagName('string')
                            if attribute:
                                text = get_text(attribute[0].childNodes)
                                attributes['level_name'] = text
                        elif property_name == 'direction':
                            attribute = custom_property.getElementsByTagName('string')
                            if attribute:
                                text = get_text(attribute[0].childNodes)
                                attributes['direction'] = text
                        elif property_name == 'sprite':
                            attribute = custom_property.getElementsByTagName('string')
                            if attribute:
                                text = get_text(attribute[0].childNodes)
                                attributes['sprite'] = text

                # Parse Path objects
                for world_points in item.getElementsByTagName('WorldPoints'):
                    # Path is stored as a list of (x, y) tuples
                    path_list = []
                    for vector2 in world_points.getElementsByTagName('Vector2'):
                        x = vector2.getElementsByTagName('X')[0]
                        x_value = int(get_text(x.childNodes))
                        y = vector2.getElementsByTagName('Y')[0] 
                        y_value = int(float(get_text(y.childNodes))) * -1 # get y to positive values
                        path_list.append((x_value, y_value))
                    attributes['path'] = path_list

                # update items dictionary with the objects info (attributes dictionary)
                items[item_name] = attributes
            # update data dictionary with the layer info (items dictionary)
            self.data[layer_name] = items

    def initiateLevel(self, entity_factory):
        """
        To be used after importXML is used.
        Uses the data extracted from the xml file to create the entities belonging
        to the level parsed.
        Parses only the terrain and the collision, the other things need to be
        parsed manually.
        Only works if the given entity_factory has the following methods:
            - createTerrain(self, x, y, sprite)
            - createCollision(self, x, y, width, height)
            - createRenderOnly(self, x, y, sprite)
            - createHero(x, y)
            - createLight
            - createObstructor(x, y, width, height)
            - createDeathZone
            - createIntermitentLight
            - createCrate

        And the xml parsed level has a correct form (look what's parsed, level
            should and must have everythin below or this method won't work)
        @entity_factory: instance of larv.EntityFactory.EntityFactory
        """
        assert isinstance(entity_factory, larv.EntityFactory)
        assert self.data != None

        # process the Background layer
        for background_element in self.data['background'].values():
            x = background_element['x']
            y = background_element['y']
            sprite = pygame.image.load(background_element['sprite'])
            entity_factory.createRenderOnly(x, y, sprite)

        # create the Terrain from the data we have
        for terrain in self.data['terrain'].values():
            x = terrain['x']
            y = terrain['y']
            sprite = pygame.image.load(terrain['sprite'])
            entity_factory.createTerrain(x, y, sprite)

        # create the Collision of the level from the data we currently have
        has_collision = self.data.get('collision', None)
        if has_collision:
            for collision in self.data['collision'].values():
                x = collision['x']
                y = collision['y']
                width = collision['width']
                height = collision['height']
                entity_factory.createCollision(x, y, width, height)

        # Process the Logic layer
        has_logic = self.data.get('logic', None)        
        if has_logic:
            camera_x_limit_right = self.data['logic']['camera_x_limit_right']['x']
            camera_x_limit_left = self.data['logic']['camera_x_limit_left']['x']
            camera_y_limit_top = self.data['logic']['camera_y_limit_top']['y']
            camera_y_limit_bottom = self.data['logic']['camera_y_limit_bottom']['y']

            player_start = (self.data['logic']['player_start']['x'],
                            self.data['logic']['player_start']['y'])
            player_finish = (self.data['logic']['player_finish']['x'],
                             self.data['logic']['player_finish']['y'])

            level_name = self.data['logic']['level_name']['level_name']

            entity_factory.createLevelInfo(camera_x_limit_right, camera_x_limit_left,
                                           camera_y_limit_top, camera_y_limit_bottom,
                                           player_start, player_finish, level_name)

            # create the Hero
            entity_factory.createHero(player_start[0], player_start[1])

        # Process the Light layer
        has_light = self.data.get('light', None)        
        if has_light:
            for name, dic in self.data['light'].items():
                # process the obstructors
                if 'ectangle' in name or 'bstructor' in name:
                    x, y, width, height = dic['x'], dic['y'], dic['width'], dic['height']
                    entity_factory.createObstructor(x, y, width, height)
                elif ('ight' in name or 'ircle' in name) and 'ntermitent' not in name:
                    alpha = dic.get('alpha', None)
                    if not alpha:
                        alpha = DEFAULT_LIGHT_ALPHA
                    entity_factory.createLight(dic['x'], dic['y'], size=dic['size'], alpha=alpha)
                elif 'ntermitent' in name:
                    alpha = dic.get('alpha', None)
                    if not alpha:
                        alpha = DEFAULT_LIGHT_ALPHA
                    entity_factory.createIntermitentLight(dic['x'], dic['y'], size=dic['size'], 
                                                          alpha=alpha, interval=dic['interval'])


        # Process the Death layer
        has_death = self.data.get('death', None)        
        if has_death:
            for name, dic in self.data['death'].items():
                # process death zones
                x, y, width, height = dic['x'], dic['y'], dic['width'], dic['height']
                entity_factory.createDeathZone(x, y, width, height)

        # Process the Items layer
        has_items = self.data.get('items', None)        
        if has_items:
            for name, dic in self.data['items'].items():
                # process crates
                if 'crate' in name:
                    x = dic['x']
                    y = dic['y']
                    sprite = pygame.image.load(dic['sprite'])
                    entity_factory.createCrate(x, y, sprite)
                # process intermitent lasers
                elif 'aser' in name and 'ntermitent' in name:
                    entity_factory.createIntermitentLaser(dic['x'], dic['y'],
                                                 dic['interval'], dic['direction'])
                # process permanent lasers
                elif 'aser' in name and 'ermanent' in name:
                    entity_factory.createPermanentLaser(dic['x'], dic['y'],dic['direction'])
                # process moving platforms
                elif 'moving' in name and 'platform' in name:
                    x, y = dic['x'], dic['y']                    
                    sprite = pygame.image.load(dic['sprite'])
                    path = dic['path']
                    # Append the same path but in inverse mode so platforms return
                    for n in range(len(path)-1, -1, -1):
                        path.append(path[n])
                    entity_factory.createMovingPlatform(x,y, dic['path'], sprite)

    def __str__(self):
        """Returns a string representation of the class (data)."""
        return pprint.pformat(self.data, indent = 1, width = 80)

if __name__ == '__main__':
    parser = XMLParser()
    parser.importXML('levels\level7.xml')
    print(parser)
