# -*- coding: UTF-8 -*-
import pygame
import pymunk
import math
import helper

from pymunk.vec2d import Vec2d
from pygame.constants import *
from ColorConstants import *
from Globals import *


############################################
############# SHADOW  ENGINE ############### Info: http://forums.tigsource.com/index.php?topic=8803.0
############################################
def getProjectedPoint(light, point, radius = None, output = 'pygame', mode = None):
    """
    Returns the projected point of the given point repective to the given light.
    @light, point: tuples or vec2d
    @radius: int, if specified, the shadow will up to the radius (supposed to be
             light radius). IT'S IMPERFECT, there are leftovers, small pieces
             undrawn.
    @output: can be pygame or pymunk (vec2d)
    @mode:
      - 1: don't check if the arguments given are vec2d's (much faster)
    """
    if mode != 1:
        if not isinstance(light, pymunk.vec2d.Vec2d):
            light = toPymunk(light)
        if not isinstance(point, pymunk.vec2d.Vec2d):
            point = toPymunk(point)

    light_to_point = point - light
    projected_point = point + light_to_point

    if radius:
        extra_length = radius - light_to_point.get_length()
        light_to_point = light_to_point.normalized()
        vector_to_add = light_to_point * extra_length
        projected_point = point + vector_to_add
        # projected_point *= 1.0075

    if output == 'pygame':
        return toPygame(projected_point)
    else:
        return projected_point

def getProjectionVerticesForLine(light, a, b, radius = None, output = 'pygame', mode = None):
    """
    Calculates and returns the projection vertices.
    Returns: 4 values: a, b, c, d
      - a = argument
      - b = argument
      - c = projected a vertex
      - d = projected b vertex
    The function is smart enough to recognize input format.

    Info: http://forums.tigsource.com/index.php?topic=8803.0
    @radius: int, if specified, the shadow will go up to the radius
    @output: can be pygame or pymunk (vec2d)
    @mode:
      - 1: don't check if the arguments given are vec2d's (much faster)
    """
    if mode != 1:
        if not isinstance(light, pymunk.vec2d.Vec2d):
            light = toPymunk(light)
        if not isinstance(a, pymunk.vec2d.Vec2d):
            a = toPymunk(a)
        if not isinstance(b, pymunk.vec2d.Vec2d):
            b = toPymunk(b)    

    c = getProjectedPoint(light, a, radius, output='pymunk', mode=1)
    d = getProjectedPoint(light, b, radius, output='pymunk', mode=1)

    if output == 'pygame':
        return toPygame(a), toPygame(b), toPygame(c), toPygame(d)
    else:
        return a, b, c, d

def doesEdgeCastShadow(light, a, b, mode = None):
    """
    Returns a boolean depending on whether or not the edge delimited by the
    given arguments should cast a shadow based on the given light.
    @light: origin, vec2d or (x, y) tuple.
    @a: first point of the segment we're evaluating.
    @b: second point of the segment we're evaluating.
    @mode:
      - 1: don't check if the arguments given are vec2d's (much faster)
    """
    if mode != 1:
        if not isinstance(light, pymunk.vec2d.Vec2d):
            light = toPymunk(light)
        if not isinstance(a, pymunk.vec2d.Vec2d):
            a = toPymunk(a)
        if not isinstance(b, pymunk.vec2d.Vec2d):
            b = toPymunk(b)  

    start_to_end = b - a
    normal = pymunk.vec2d.Vec2d(-1 * start_to_end.y, start_to_end.x)
    light_to_start = a - light

    if normal.dot(light_to_start) > 0:
        return True
    else:
        return False

def drawShadowFromVertices(surface, light, vertices, radius=None, color=BLACK, alpha=136, mode=None):
    """
    Draws the shadow from the given vertices depending on their position relative
    to the given light.
    @light: light position in a (x, y) tuple or a vec2d.
    @vertices: MUST be ordered clockwise, list/tuple of vertices.
    @color: color in which the shadow will be drawn.
    @alpha: the alpha (1..255) that will be applied to the shadow.
    @mode:
      - 1: don't check if the arguments given are vec2d's (much faster)
    """
    vertices = list(vertices)
    if mode != 1:
        if not isinstance(light, pymunk.vec2d.Vec2d):
            light = toPymunk(light)
        for n in range(len(vertices)):
            if not isinstance(vertices[n], pymunk.vec2d.Vec2d):
                vertices[n] = toPymunk(vertices[n])

    if not isinstance(color, pygame.Color):
        r,g,b = color
        color = pygame.Color(r,b,g)
    else:
        color = copy.copy(color)
    color.a = alpha

    transparent_surface = surface.convert_alpha() #without this we can't draw transparencies

    vertices.append(vertices[0])
    for n in range(len(vertices)-1):
        first, last = vertices[n], vertices[n+1]
        if doesEdgeCastShadow(light, first, last): #if shadow should be drawn
            # we get the vertices to draw the shadow polygon
            a,b,c,d = getProjectionVerticesForLine(light, first, last, radius=radius,
                                                   output = 'pygame', mode = 1)
            # we arrange the vertices clock wise order
            vertices_to_draw = (a, c, d, b) # clock wise
            pygame.draw.polygon(transparent_surface, color, vertices_to_draw)
    surface.blit(transparent_surface, (0,0))

############################################
############## LIGHT  ENGINE ###############
############################################
class Light:
    """
    Provides a way to simulate light interfering with rectangles (other shapes
    may be smartly modeled as rectangles just for the lightning sake).
    Works in PYGAME COORDINATES, aka 0,0 is topleft of the screen.

    Usage:
     - Create your light using the constructor: l = Light(x, y, size, alpha)
            x and y are the center of the light, size is the radius.
     - Create your mask: l.createMask()
     - Add your obstructors (shadow casters, things that light won't traspass)
     - Whenever light position changes -> l.setLightPosition(x, y)
     - Before blitting -> l.update()
            WARNING: may not need to update every frame! it's expensive!
     - Whenever you want to blit l.blit(surface_to_blit)
    """
    def __init__(self, x, y, size = 100, alpha = None, color = WHITE, gradient = False):
        """
        @x,y: light position (middle)
        @size: radius of the light
        @alpha: if given (1..255), light will be drawn with some transparency.
        @color: color of the light.
        @gradient: indicates whether light will be drawn with a gradient or not.
        """
        self.x = x
        self.y = y
        self.size = size

        self.obstructors = []
        self.obstructor_segments = []

        # Data structures used for tracting with dynamic objects for extra efficiency
        self.auxiliar_obstructors = []
        self.auxiliar_obstructor_segments = []

        # Data structures that allow us to update the obstructors with the camera
        self.clean_obstructors = [] 
        self.mode = 'dirty'    # changed by updateObstructors to dirty

        self.light_rect = None
        self.mask = None
        self.color = color
        self.gradient = gradient

        if alpha:
            if 1 <= alpha <= 255:
                self.alpha = alpha
            else:
                raise ValueError('Alpha must be between 1 and 255')
        else:
            self.alpha = None

    def addObstructor(self, rect, auxiliar = False):
        """
        Adds a obstructor to the light engine.
        @rect: pygame.rect object.
        @auxiliar: bool, adds the rect to a different list if given.
        """
        top_left = rect.topleft
        top_right = rect.topright
        bottom_right = rect.bottomright
        bottom_left = rect.bottomleft

        if auxiliar:
            self.auxiliar_obstructors.append(rect)        

            self.auxiliar_obstructor_segments.append((top_left, top_right))
            self.auxiliar_obstructor_segments.append((top_right, bottom_right))
            self.auxiliar_obstructor_segments.append((bottom_right, bottom_left))
            self.auxiliar_obstructor_segments.append((bottom_left, top_left))
        else:
            self.obstructors.append(rect)            

            self.obstructor_segments.append((top_left, top_right))
            self.obstructor_segments.append((top_right, bottom_right))
            self.obstructor_segments.append((bottom_right, bottom_left))
            self.obstructor_segments.append((bottom_left, top_left))

    def setObstructors(self, rects, auxiliar = False):
        """
        Changes the actual obstructors by the ones that are inside the given
        iterator (set, list, etc).
        @rects: iterator, contains pygame.rect objects.
        @auxiliar: bool, adds the rect to a different list if given.
        """
        if auxiliar:
            self.auxiliar_obstructors = []
            self.auxiliar_obstructor_segments = []
            for rect in rects:
                self.addObstructor(rect, auxiliar=True)

        else:
            self.obstructors = []
            self.obstructor_segments = []
            for rect in rects:
                self.addObstructor(rect, auxiliar=False)

    def cleanAuxiliar(self):
        self.auxiliar_obstructors = []
        self.auxiliar_obstructor_segments = []

    def tracePoint(self,x1,y1,x2,y2,l):
        """
        Only used from getPolygon
        """
        theta = math.atan2((y2-y1),(x2-x1));    
        if theta<0:
            d= (180*(theta+(math.pi*2))/math.pi)
        else:
            d= (180*(theta)/math.pi)
        dx = math.cos(math.radians(d))
        dy = math.sin(math.radians(d))                
    
        return (x2+dx*l,y2+dy*l)

    def getPolygon(self,x,y,box):
        """
        Only used from drawMask with arguments:
            getPolygon(self.size,self.size,r)
        where r is the new_rect that was first cropped and then reallocated.
        """
    
        r = box.right
        l = box.left
        t = box.top
        b = box.bottom
        L = self.size+10
        
        tracePoint = self.tracePoint
            
        box = pygame.Rect(l,t,box.width-1,box.height-1)
        
        lightPos = (self.size,self.size)
               
        if x >= l and x <= r:
            if y >= b: # directly under
                #print "UNDER"
                tp1 = tracePoint(x,y,l,b,L)
                tp2 = tracePoint(x,y,r,b,L)
                return ((box.bottomleft,tp1,[lightPos[0]-L,lightPos[1]-L],[lightPos[0]+L,lightPos[1]-L],tp2,box.bottomright))
            else:   # directly above             
                #print "ABOVE"
                tp1 = tracePoint(x,y,l,t,L)
                tp2 = tracePoint(x,y,r,t,L)
                return ((box.topleft,tp1,[lightPos[0]-L,lightPos[1]+L],[lightPos[0]+L,lightPos[1]+L],tp2,box.topright))
        elif y >= t and y <= b:
            if x <= l: # directly to the left
                #print "LEFT"
                tp1 = tracePoint(x,y,l,b,L)
                tp2 = tracePoint(x,y,l,t,L)
                return ((box.bottomleft,tp1,[lightPos[0]+L,lightPos[1]+L],[lightPos[0]+L,lightPos[1]-L],tp2,box.topleft))
            else:   # directly to the right
                #print "RIGHT"
                tp1 = tracePoint(x,y,r,b,L)
                tp2 = tracePoint(x,y,r,t,L)
                return ((box.bottomright,tp1,[lightPos[0]-L,lightPos[1]+L],[lightPos[0]-L,lightPos[1]-L],tp2,box.topright))
        if y <= t:
            if x <= l: # upper left
                #print "UPPER LEFT"
                tp1 = tracePoint(x,y,r,t,L)
                tp2 = tracePoint(x,y,l,b,L)
                return ((box.topleft,box.topright,tp1,tp2,box.bottomleft))
            else:     # upper right
                #print "UPPER RIGHT"
                tp1 = tracePoint(x,y,l,t,L)
                tp2 = tracePoint(x,y,r,b,L)
                return ((box.topright,box.topleft,tp1,tp2,box.bottomright))
        elif y >= b:
            if x <= l: # lower left
                #print "LOWER LEFT"
                tp1 = tracePoint(x,y,r,b,L)
                tp2 = tracePoint(x,y,l,t,L)
                return ((box.bottomleft,box.bottomright,tp1,tp2,box.topleft))
            else:     # lower right
                #print "LOWER RIGHT"
                tp1 = tracePoint(x,y,l,b,L)
                tp2 = tracePoint(x,y,r,t,L)
                return ((box.bottomright,box.bottomleft,tp1,tp2,box.topright))
                
        return None      

    def update(self):
        """
        Previously drawMask.
        The core of the engine, calculates the parts of the light which are
        obfuscated by the obstructors and doesn't light those.
        Stores the results in self.mask (which is a pygame.surface).
        """
        img = self.mask
        nrects = []
        # Iterate over all the rects
        # If one is colliding with light rect, it gets cropped and then moved,
        # and added to nrects list
        if self.mode == 'dirty':
            obstructors_list = self.obstructors + self.auxiliar_obstructors
        elif self.mode == 'clean':
            obstructors_list = self.clean_obstructors + self.auxiliar_obstructors
        else:
            raise ValueError('Invalid mode')

        for r in obstructors_list:
            if self.light_rect.colliderect(r):
                nr = r.clip(self.light_rect) # Returns a new rectangle that is cropped to be completely inside the argument Rect.
                # Normalize the rectangle(move it near to 0,0 for following comparisons)
                # Imagine a new rectangle at top left of size light_size*light_size,
                # which is the mask, the rectangles are moved there.
                nr.top = nr.top - self.light_rect.top
                nr.left = nr.left - self.light_rect.left
                nrects.append(nr)
        
        img.fill(1) # black, which is set to transparent before
        # draws the light circle
        if self.gradient:
            def f(x):
                # return ((x*x))
                return math.sqrt(x) - 0.1
                # return math.exp(x)
                # return -math.cos(x/1.2)
                # return 0.49*math.cos(10*x)+0.5
                # return math.exp(-x/10.)*math.sin(x)
                # return math.ceil(x/10.)
                # return math.exp(x-10)+math.exp(-x-10)
                # return x**2-x**4
                # return 10*x+10

            def f2(x):
                return x
                return math.sqrt(x) - 0.1
                # return math.exp(x)

            start = (self.size, self.size)
            end = (self.size*2, self.size)
            start_color = self.color
            end_color = (0,0,0)
            mode = 1
            g_func = f
            r_func = f
            b_func = f
            a_func = f2
            draw_circle(img, start, end, start_color, end_color, mode = mode, Afunc=a_func)
                        # Rfunc = r_func, Gfunc = g_func, Bfunc = b_func, Afunc = a_func)
        else:
            pygame.draw.circle(img, self.color, (self.size,self.size), self.size,0)
        
        # iterates over all the rects (which were found colliding, were cropped and moved)
        for r in nrects:
            # if r.collidepoint(self.x, self.y):
            #     img.fill(1)
            #     return
            p = self.getPolygon(self.size,self.size,r)                
            if p:
                pygame.draw.polygon(img, 1, p, 0)
        
        # draws the center of the light - the light 'producer'
        # pygame.draw.circle(img, 3, (self.size,self.size), 2)

    def updateObstructors(self, camera_x, camera_y):
        """
        Updates position of the obstructors given a camera x and y.
        @x,y: camera_x and camera_y.
        """
        self.mode = 'clean'
        self.clean_obstructors = []
        for obstructor in self.obstructors:
            x, y = obstructor.topleft
            clean_obstructor = obstructor.copy()
            x -= camera_x
            y += camera_y
            clean_obstructor.topleft = (x, y)
            self.clean_obstructors.append(clean_obstructor)
    
    def drawMap(self,surface, color = BLACK):
        """
        Helper method, draws all the obstructors on the given surface.
        Very useful for debugging.
        """
        # img.fill((100,100,100))
        for r in self.obstructors:
            pygame.draw.rect(surface, color, r, 0)

    def createMask(self):
        """
        This method is highly customizable, serves the purpose of changing
        the aesthetic of the light.
        """
        mask = pygame.Surface([self.size*2,self.size*2],HWSURFACE)#|HWPALETTE,8)        
        # mask.set_palette([[0,0,0],[255,0,0],[180,180,180],[255,255,255]])
        mask.set_colorkey(1, RLEACCEL) # 1 will be transparent
        self.light_rect = mask.get_rect()
        self.light_rect.center = (self.x, self.y)
        if self.alpha:
            mask.set_alpha(self.alpha)
        self.mask = mask 

    def setLightPosition(self, x, y):
        """
        Warning: give coordinates in pygame's mode.
        """
        self.x = x
        self.y = y
        self.light_rect.center = (self.x, self.y)

    def blit(self, surface):
        """
        Paints the current mask into the given surface.
        """
        surface.blit(self.mask, self.light_rect.topleft)

    def isRectInsideLight(self, rect, x, y, camera_x=0, camera_y=0):
        """
        Warning: Brute force approach! Assume low perfomance.
        Returns a boolean depending whether it is inside the casted light or
        not.
        Tests every rect vertex against every segment formed by the obstructors.
        @rect: pygame.Rect instance.
        @x,y: designed to be light x and y coordinates after applying camera
              offsets.
        """
        top_left = rect.topleft
        top_right = rect.topright
        bottom_right = rect.bottomright
        bottom_left = rect.bottomleft
        vertices = [top_left, top_right, bottom_right, bottom_left]
        # vertices = [rect.center]

        # adjust segments to camera values
        # print(camera_x, camera_y)
        if camera_x or camera_y:
            segments_aux = []
            for segment in self.obstructor_segments + self.auxiliar_obstructor_segments:
                a = segment[0]
                b = segment[1]
                first_point = (a[0]-camera_x, a[1]+camera_y)
                second_point = (b[0]-camera_x, b[1]+camera_y)
                segments_aux.append((first_point, second_point))
        else:
            segments_aux = list(self.obstructor_segments)
        # n = 1
        # print(segments_aux[n], self.obstructor_segments[n])

        # DEBUG
        # pygame.draw.circle(DISPLAYSURF, RED, rect.center, 5)
        # for segment in segments_aux:
        #     pygame.draw.line(DISPLAYSURF, RED, segment[0], segment[1], 5)
        #     pygame.draw.line(DISPLAYSURF, BLUE, rect.center,(x, y), 3)



        # remove irrelevant vertices (far away)
        for i in range(len(vertices)-1,-1,-1):
            vertex = vertices[i]
            # distance formula
            if math.sqrt( (vertex[0]-x)**2 + (vertex[1]-y)**2 ) > self.size:
                vertices.pop(i)

        # we check if we have any vertex near light max range (optimization)
        if len(vertices) > 0:
            # iterate over obstructor segments 
            for segment in segments_aux:
                # segment to test
                C = segment[0]
                D = segment[1]
                # For each segment, test against each rect vertex.
                # If they intersect, then that vertex isn't relevant anymore,
                # because he's blocked from light (light doesn't reach that
                # vertex), so we're free to remove it from the list.
                for i in range(len(vertices)-1,-1,-1):
                    # second segment
                    A = vertices[i]
                    B = (x, y)
                    if Light.doSegmentsIntersect(A, B, C, D):
                        vertices.pop(i)

        # At the end of the algorithm, we have removed all the irrelevant 
        # vertices of the list, so if there was any relevant one, then we can
        # assume that the vertex of the rectangle (and thus, the rectangle
        # itself) is affected by the light.
        return len(vertices) > 0

    @staticmethod
    def doSegmentsIntersect(A, B, C, D):
        """
        Fins if two segments intercept or not (returns Bool).
        Two segments are: AB and CD.
        @A, B, C, D: points in tuple mode (x, y)
        """
        def ccw(A,B,C):
            """Helper method."""
            # return (C.y-A.y) * (B.x-A.x) > (B.y-A.y) * (C.x-A.x)
            return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

        return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)



###### LIGHT GRADIENT #######

def draw_circle(surface, startpoint, endpoint, startcolor, endcolor, Rfunc = (lambda x:x), Gfunc = (lambda x:x), Bfunc = (lambda x:x), Afunc = (lambda x:1), mode=0):
    """
    Gradient.
    Instead of returning an Surface, this function draw it directy onto the 
    given Surface and returns the rect.
    """
    dx = endpoint[0]-startpoint[0]
    dy = endpoint[1]-startpoint[1]
    radius = int(round(math.hypot(dx, dy)))
    pos = (startpoint[0]-radius, startpoint[1]-radius)
    # if BLEND_MODES_AVAILABLE:
    return surface.blit(radial_func(radius, startcolor, endcolor, Rfunc, Gfunc, Bfunc, Afunc), pos, None, mode)
    # else:
    #     return surface.blit(radial_func(radius, startcolor, endcolor, Rfunc, Gfunc, Bfunc, Afunc), pos)

def radial_func(radius, startcolor, endcolor, Rfunc = (lambda x:x), Gfunc = (lambda x:x), Bfunc = (lambda x:x), Afunc = (lambda x:1), colorkey=(0,0,0,0)):
    """
    Draws a linear raidal gradient on a square sized surface and returns
    that surface.
    """
    bigSurf = pygame.Surface((2*radius, 2*radius)).convert_alpha()
    if len(colorkey)==3:
        colorkey += (0,)
    bigSurf.fill(colorkey)
    color = ColorInterpolator(radius, startcolor, endcolor, Rfunc, Gfunc, Bfunc, Afunc)
    draw_circle = pygame.draw.circle
    for rad in range(radius, 0, -1):
        draw_circle(bigSurf, color.eval(rad), (radius, radius), rad)
    return bigSurf

class ColorInterpolator(object):
    '''
    ColorInterpolator(distance, color1, color2, rfunc, gfunc, bfunc, afunc)
    
    interpolates a color over the distance using different functions for r,g,b,a
    separately (a= alpha).
    '''
    def __init__(self, distance, color1, color2, rfunc, gfunc, bfunc, afunc):
        object.__init__(self)
        
        self.rInterpolator = FunctionInterpolator(color1[0], color2[0], distance, rfunc)
        self.gInterpolator = FunctionInterpolator(color1[1], color2[1], distance, gfunc)
        self.bInterpolator = FunctionInterpolator(color1[2], color2[2], distance, bfunc)
        if len(color1)==4 and len(color2)==4:
            self.aInterpolator = FunctionInterpolator(color1[3], color2[3], distance, afunc)
        else:
            self.aInterpolator = FunctionInterpolator(255, 255, distance, afunc)
            
    def eval(self, x):
        '''
        eval(x) -> color
        
        returns the color at the position 0<=x<=d (actually not bound to this interval).
        '''
        return [self.rInterpolator.eval(x), 
                self.gInterpolator.eval(x), 
                self.bInterpolator.eval(x), 
                self.aInterpolator.eval(x)]

class FunctionInterpolator(object):
    '''
    FunctionINterpolator(startvalue, endvalue, trange, func)
    
    interpolates a function y=f(x) in the range trange with
    startvalue = f(0)
    endvalue   = f(trange)
    using the function func
    '''
    def __init__(self, startvalue, endvalue, trange, func):
        object.__init__(self)
        # function
        self.func = func
        # y-scaling
        self.a = endvalue-startvalue
        if self.a == 0:
            self.a = 1.
        # x-scaling
        if trange!=0:
            self.b = 1./abs(trange)
        else:
            self.b = 1.
        # x-displacement
        self.c = 0
        # y-displacement
        self.d = min(max(startvalue,0),255)
        
    def eval(self, x):
        ''' 
        eval(x)->float
        
        return value at position x
        '''
        # make sure that the returned value is in [0,255]
        return int(min(max(self.a*self.func(self.b*(x+self.c))+self.d, 0), 255))



if __name__ == '__main__':
    pass
