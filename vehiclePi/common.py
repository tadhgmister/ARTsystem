from __future__ import annotations
import math
from enum import Enum

class MOVE(Enum):
    """movement commands sent to arduino to move the motors one step."""
    F = "Forward" #both wheels forward
    R = "Turn right in place" #left wheel forward, right wheel back
    L = "Turn left in place" #right wheel forward, left wheel back
    FR= "turn right moving forward" #only left wheel forward
    FL= "turn left moving forward" #only right wheel forward
    
    B = "backwards" #both wheels backward
    BR = "backwards right" #left wheel backwards
    BL = "backwards left" #right wheel backwards

class OPCODE(Enum):
    """
    The int values of all expected packet types.
    """
    STANDBY = 0 #Standy request packet
    CALIBRATE = 1 #Calibration request/instruction packets
    TRACK = 2   #Drawing request(from app)/tracking request(to Tower) packets
    POSITION = 3 #Position request packet (for sync_position)
    NEXTPOS = 4 #Get next step/line request
    ACK = 5
    ERROR = 6   #For any errors.  Error packets should contain an info string.

class Position:
    """position of the car - coordinates and facing direction"""
    __slots__ = ["x","y","facing"]
    x: float
    "x position of car relative to tower in cm"
    y: float
    "y position of car relative to tower in cm" 
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
