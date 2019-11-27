from __future__ import annotations
from enum import Enum

class OPCODE(Enum):
    """
    The int values of all expected packet types.
    """
    STANDBY = 0
    CALIBRATE = 1
    TRACK = 2
    POSITION = 3
    NEXTPOS = 4
    ACK = 5
    ERROR = 6

class Position:
    """position of the car - coordinates and facing direction"""
    __slots__ = ["x","y","facing"]
    x: float
    "x position of car relative to tower in mm"
    y: float
    "y position of car relative to tower in mm" 
    facing: float
    "angle car is facing in radians measured from positive x towards positive y"

    def __init__(self, x,y,facing=0):
        self.x = x
        self.y = y
        self.facing = facing
        
    def moved_forward(self, distance: "moves in facing direction") -> Position:
        """ returns a new position moved by given distance in current facing direction"""
        newx = self.x + distance * math.cos(self.facing)
        newy = self.y + distance * math.sin(self.facing)
        return Position(newx, newy, self.facing)
    
    def turned(self,angle: "radians to turn") -> Position:
        """ returns a new position turned by given angle (radians) """
        return Position(self.x, self.y, self.facing + angle)
