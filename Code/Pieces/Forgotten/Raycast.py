import pygame
from pygame.locals import *
import pymunk
from pymunk.vec2d import Vec2d
import math

from ColorConstants import *
from helper import *
import helper

##### RAYCASTING : http://www.redblobgames.com/articles/visibility/
class Raycast:
    """
    Provides a method to form light from a source up to given obstacles.
    Based on a system that gets information on what the central point (light)
    can 'see' (field of vision).

    Usage:
      - Create an instance of the class: raycast = Raycast()
      - Add the rects or segments that should block the light.
            - raycast.addSegment
            - raycast.addRect(rect)
            - raycast.addRectList(rect_list)
      - Add the limits of the light: raycast.setBorder(x, y, width, height, input)
      - Set the light location using: raycast.setLightLocation(x, y, input)
      - Update the light using: raycast.sweep()
      - Then you can draw the result using raycast.blit(surface, color, alpha)
    """
    def __init__(self):
        self.segments = []
        self.endpoints = []
        self.center = Vec2d(0, 0)
        self.output = []
        self.open = []
        self.size = 0

    #### ENGINE
    @staticmethod
    def leftOf(s, p):
        """
        Returns a boolean depending on if the point is situated to the left in 
        comparison to the segment.
        @s: Segment instance
        @p: vec2d (point)
        """
        cross = (s.p2.x - s.p1.x)*(p.y - s.p1.y) - (s.p2.y -s.p1.y)*(p.x - s.p1.x)
        return cross < 0

    @staticmethod
    def interpolate(p, q, f):
        """
        Calculates: p*(1-f) + q*f
        @p, q: vec2d (points)
        @f: float
        """
        return Vec2d(p.x*(1-f) + q.x*f, p.y*(1-f) + q.y*f)

    @staticmethod
    def _segment_in_front_of(a, b, relative_to):
        """
        Returns a boolean depending on if segment a is in front of segment b.
        Warning: not anti_simmetric:
            _segment_in_front_of(a, b) != (!_segment_in_front_of(b, a))
        @a, b: Segment instances
        @relative_to: vec2d
        """
        # Slighly shorten the segments so that intersections of endpoints don't
        # count as intersections in this algorthm.
        A1 = Raycast.leftOf(a, Raycast.interpolate(b.p1, b.p2, 0.01))
        A2 = Raycast.leftOf(a, Raycast.interpolate(b.p2, b.p1, 0.01))
        A3 = Raycast.leftOf(a, relative_to)
        B1 = Raycast.leftOf(b, Raycast.interpolate(a.p1, a.p2, 0.01))
        B2 = Raycast.leftOf(b, Raycast.interpolate(a.p2, a.p1, 0.01))
        B3 = Raycast.leftOf(b, relative_to)

        # Consider line A1-A2
        # If both B1 and B2 are on one side and relative_to is on the other side,
        # then A is in between the viewer and B.
        # We can do the same with B1-B2
        # If A1 and A2 are on one side, and relative_to is on the other side, then
        # B is in between the viewer and A
        if B1 == B2 and B2 != B3: return True
        if A1 == A2 and A2 == A3: return True
        if A1 == A2 and A2 != A3: return False
        if B1 == B2 and B2 == B3: return False

        # If A1 != A2 and B1 != B2 then we have a intersection.
        return False

    def sweep(self, max_angle = 999.0):
        """
        Run the algorithm.
        Sweeps around a circle to find which areas are to be drawn.
        Fills the output list with vertices of the triangles to be drawn.
        @max_angle: in degrees, maximum angle evaluated.
        """
        self.output = [] #restart
        self.open = []

        self.endpoints.sort(key=lambda p: (p.angle, not p.begin))
        begin_angle = 0.0

        for i in (0,1):
            for p in self.endpoints:
                current_old = (None if len(self.open) == 0
                                    else self.open[0])
                if p.begin:
                    # Insert into the right place in the list
                    count = 0
                    for n in range(len(self.open)):
                        count = n
                        segment = self.open[n]
                        if not Raycast._segment_in_front_of(p.segment, segment, self.center):
                            break
                    self.open.insert(count, p.segment)
                elif p.segment in self.open:
                    self.open.remove(p.segment)

                current_new = (None if len(self.open) == 0
                                    else self.open[0])
                if current_old != current_new:
                    if i == 1:
                        self.addTriangle(begin_angle, p.angle, current_old)
                    begin_angle = p.angle

    @staticmethod
    def lineIntersection(p1, p2, p3, p4):
        """
        Info: http://paulbourke.net/geometry/lineline2d/
        @arguments: vec2d
        """
        try:
            s = ((p4.x - p3.x) * (p1.y - p3.y) - (p4.y - p3.y) * (p1.x - p3.x))/ \
                ((p4.y - p3.y) * (p2.x - p1.x) - (p4.x - p3.x) * (p2.y - p1.y))
        except ZeroDivisionError:
            s = 0
        return Vec2d(p1.x + s*(p2.x - p1.x), p1.y + s*(p2.y - p1.y))

    def addTriangle(self, angle1, angle2, segment):
        """
        Stores the triangle formed by the given angles and the given segment into
        the output list.
        @angle1, angle2: degrees
        @segment: Segment instance.
        """
        p1 = self.center # vec2d
        p2 = Vec2d(self.center.x + math.cos(angle1), self.center.y + math.sin(angle1))
        p3 = Vec2d(0,0)
        p4 = Vec2d(0,0)

        if segment != None:
            # Stop the triangle at the intersecting segment
            p3.x = segment.p1.x
            p3.y = segment.p1.y
            p4.x = segment.p2.x
            p4.y = segment.p2.y
        else:
            # raise ValueError('Read comments at this exact line.')
            # // Stop the triangle at a fixed distance; this probably is
            # // not what we want, but it never gets used in the demo
            p3.x = self.center.x + math.cos(angle1) * 500
            p3.y = self.center.y + math.sin(angle1) * 500
            p4.x = self.center.x + math.cos(angle2) * 500
            p4.y = self.center.y + math.sin(angle2) * 500

        p_begin = Raycast.lineIntersection(p3, p4, p1, p2)

        p2.x = self.center.x + math.cos(angle2)
        p2.y = self.center.y + math.sin(angle2)

        p_end = Raycast.lineIntersection(p3, p4, p1, p2)

        points = (p_begin, p_end)
        self.output.append(points)

    #### CONVENIENCE METHODS
    def addSegment(self, point1, point2, border=False):
        """
        @point1, point2: vec2d instances.
        """
        if not isinstance(point1, Vec2d):
            point1 = Vec2d(point1[0], point1[1])
        if not isinstance(point2, Vec2d):
            point2 = Vec2d(point2[0], point2[1])

        segment = None
        p1 = EndPoint(x=0, y=0, begin=False, segment=segment, angle=0.0)
        p2 = EndPoint(x=0, y=0, begin=False, segment=segment, angle=0.0)

        segment = Segment(p1, p2, 0.0)
        p1.x = point1.x
        p1.y = point1.y
        p2.x = point2.x
        p2.y = point2.y        
        segment.p1 = p1
        segment.p2 = p2
        p1.segment = segment
        p2.segment = segment

        self.segments.append(segment)
        self.endpoints.append(p1)
        self.endpoints.append(p2)

    def addRect(self, rect, border=False):
        """
        Adds the given rect to the engine.
        @rect: pygame.Rect instance.
        """
        assert isinstance(rect, pygame.Rect)
        top_left = rect.topleft
        bottom_left = rect.bottomleft
        top_right = rect.topright
        bottom_right = rect.bottomright

        self.addSegment(top_left, bottom_left, border)
        self.addSegment(bottom_left, bottom_right, border)
        self.addSegment(bottom_right, top_right, border)
        self.addSegment(top_right, top_left, border)  

    def addRectList(self, rect_list, border=False):
        """
        Given a list of pygame.Rect objects, adds all of them to the engine.
        """
        for rect in rect_list:
            self.addRect(rect, border)

    def setBorder(self, x, y, width, height, input = 'pygame'):
        """
        Adds the outer limit of the light.
        @x,y: coordinates of top_left (see input)
        @width, height: int
        @input: can be either 'pygame' or 'pymunk' (0,0 top_left, 0,0 bottom_left)
        """
        if input == 'pymunk':
            x, y = helper.toPygame(Vec2d(x,y)) 

        x = x - width//2
        y = y - height//2      
        border_rect = pygame.Rect(x, y, width, height, border=True)
        self.addRect(border_rect)

    def setBorderWithSize(self, x, y, size, input = 'pygame'):
        """
        Adds the outer limit of the light.
        @x,y: coordinates of top_left (see input)
        @size: int
        @input: can be either 'pygame' or 'pymunk' (0,0 top_left, 0,0 bottom_left)
        """
        if input == 'pymunk':
            x, y = helper.toPygame(Vec2d(x,y))
        x = x - size//2
        y = y - size//2       
        border_rect = pygame.Rect(x, y, size, size, border=True)
        self.addRect(border_rect)

    def setLightLocation(self, x, y, input = 'pygame'):
        """
        @x,y: light coordinates
        @input: can be either pygame ((0,0) topleft) or pymunk((0,0) bottomleft)
        """
        if input == 'pygame':
            self.center = Vec2d(x, y)
        elif input == 'pymunk':
            x, y = helper.toPygame(Vec2d(x, y))
            self.center = Vec2d(x, y)
        else:
            raise ValueError('bad input argument')

        for segment in self.segments:
            dx = 0.5 * (segment.p1.x + segment.p2.x) - x
            dy = 0.5 * (segment.p1.y + segment.p2.y) - y
            segment.d = dx*dx + dy*dy

            segment.p1.angle = math.atan2(segment.p1.y - y, segment.p1.x - x)
            segment.p2.angle = math.atan2(segment.p2.y - y, segment.p2.x - x)

            d_angle = segment.p2.angle - segment.p1.angle
            if d_angle <= -math.pi:
                d_angle += math.pi * 2
            if d_angle > math.pi:
                d_angle -= math.pi * 2

            segment.p1.begin = (d_angle > 0.0)
            segment.p2.begin = not segment.p1.begin  

    def blit(self, surface, color = WHITE, alpha = None):
        """
        Blits the output of the sweep algorithm into the given surface.
        """
        copied = surface.copy() # convert imporves render speed
        if alpha:
            copied.set_alpha(alpha)

        center = self.center
        for vertices in self.output:
            v1 = vertices[0]
            v2 = vertices[1]
            vertices_draw = (center, v1,v2, center)
            pygame.draw.polygon(copied, color, vertices_draw)

        surface.blit(copied, (0,0))

    def clean(self):
        """Empties containers."""
        self.segments = []
        self.endpoints = []

    def isRectInsideLight(self, rect):
        """
        WARNING: brute force approach, probably couldn't be more ineficient than
                 this.
        Returns a boolean depending on whether the given rect is inside the light
        range.
        To be used after sweep() is used, else will return always False.
        More info at: http://www.bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
        @rect: pygame.Rect instance
        """
        def ccw(A,B,C):
            """Helper method."""
            # return (C.y-A.y) * (B.x-A.x) > (B.y-A.y) * (C.x-A.x)
            return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
            
        # get rectangle segments
        seg1 = (rect.topleft, rect.topright)
        seg2 = (rect.topright, rect.bottomright)
        seg3 = (rect.bottomright, rect.bottomleft)
        seg4 = (rect.bottomleft, rect.topleft)
        segments = (seg1, seg2, seg3, seg4)

        # get triangle segments
        center = (self.center.x, self.center.y)
        for vertices in self.output:
            v1 = (vertices[0].x, vertices[0].y)
            v2 = (vertices[1].x, vertices[1].y)
            triangle_seg1 = (center, v1)
            triangle_seg2 = (v1, v2)
            triangle_seg3 = (v2, center)
            triangle_segments = (triangle_seg1, triangle_seg2, triangle_seg3)

            # test against every rect segment
            for segment_rect in segments:
                for segment_triangle in triangle_segments:
                    # return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)
                    A = segment_rect[0]
                    B = segment_rect[1]
                    C = segment_triangle[0]
                    D = segment_triangle[1]
                    if ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D):
                        return True
        return False

class Segment:
    def __init__(self, p1, p2, d = 0.0):
        """
        @p1, p2: must be EndPoint instances
        @d: distance (float)
        """
        self.p1 = p1
        self.p2 = p2
        self.d = d

class EndPoint:
    def __init__(self, x, y, begin, segment, angle):
        """
        @x, y: position
        @begin: boolean
        @segment: Segment instance
        @angle: in degrees
        """
        self.x = x
        self.y = y
        self.begin = begin
        self.segment = segment
        self.angle = angle

    def __str__(self):
        string = 'EndPoint <x,y = {0},{1}, begin={2}, seg={3}, angle={4}>'.format(
                         self.x, self.y, self.begin, self.segment, self.angle)
        return string