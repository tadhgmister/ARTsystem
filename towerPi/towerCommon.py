from __future__ import annotations
from enum import Enum

class OPCODE(Enum):
    """
    The int values of all of the request types the Towercan receive.
    """
    STANDBY = 0
    CALIBRATE = 1
    TRACK = 2
    POSITION = 3
    NEXTPOS = 4
    ACK = 5
    ERROR = 6

class Position:
    """position of the car"""
    # not sure if this is necessary
    __slots__ = ["x","y","facing"]
    x: float
    "x position of car relative to tower in mm"
    y: float
    "y position of car relative to tower in mm"
    facing: float
    "angle car is facing in radians measured from positive x towards positive y"
