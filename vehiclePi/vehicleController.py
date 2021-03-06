from __future__ import annotations
"""
controller for the vehicle program to move the car.

Version 1.1: Added a socket to the class for UDP communication
"""
import typing
import socket
try:
    from common import Position, MOVE
    from towerCommunication import sync_position
except ImportError:
    from .common import Position, MOVE
    from .towerCommunication import sync_position

class Controller:
    """
This class maintains the position and orientation of the vehicle 
Note that this class does not actually send commands to the arduino to move the car
(just because of how the project got developed in segments) so use serialCommunication for that."""
    #TODO: get actual increments for these.
    WHEEL_STEP_INCREMENT: typing.ClassVar[float] = 0.5
    "cm wheel moves per step."
    WHEEL_TURN_INCREMENT: typing.ClassVar[float] = 0.1
    "radians turned when turning wheel"
    position: Position = None
    "current position of the car relative to the tower, TODO: initial value?"
    drawing: bool = None #initially not True or False so that the shortcut in set_chalk will never ignore the first instruction.
    "whether the chalk is down so vehicle is drawing or not."
    # socket to be used for UDP communication with the tower.
    sock: Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def __init__(self, initial_position=None):
        # should this take position as input or do we even know where the car is at this point?
        self.position = initial_position

    def correct_actual_position(self, current_step: int) -> None:
        """
        requests tower to find the car's exact position and updates own internal x,y,facing variables
        this will make a call to the tower and block all operations until tower returns with answer
        it will also send the current location (calculated based on ideal conditions) for logging purposes
        """
        try:
            self.position = sync_position(self.position, current_step, self.sock)
        except Exception as e:
            print("got error", e)
        
    def move(self, instruction: MOVE):
        self._fail_if_not_initialized()
        if instruction is MOVE.F:
            self.position = self.position.moved_forward(self.WHEEL_STEP_INCREMENT)
        elif instruction is MOVE.R:
            self.position = self.position.turned( - self.WHEEL_TURN_INCREMENT)
        elif instruction is MOVE.L:
            self.position = self.position.turned(self.WHEEL_TURN_INCREMENT)
        elif instruction in (MOVE.CHALK_DOWN, MOVE.CHALK_UP):
            self.set_drawing(instruction == MOVE.CHALK_DOWN)
        else:
            raise NotImplementedError(f"invalid movement: {instruction!r}")
        
    def _fail_if_not_initialized(self):
        if self.position is None:
            raise Exception("tried to move car before initializing position")
        
    def move_forward(self) -> None:
        """ sends movement control to arduino to move forward
        then update own x,y coordinates to match
        """
        self.move(MOVE.F)

    def turn_left(self) -> None:
        """ sends motor control to arduino to turn in place CCW
        updates facing variable to match
        """
        self.move(MOVE.L)

    def turn_right(self) -> None:
        """ sends motor control to arduino to turn in place CW
        updates facing variable to match
        """
        self.move(MOVE.R)

    def forward_right(self) -> None: #typing.NoReturn
        """ moves left wheel forward one increment to turn right"""
        raise NotImplementedError("not expected to use?")
    def forward_left(self) -> None: #typing.NoReturn
        """ moves right wheel forward one increment to turn lefT"""
        raise NotImplementedError("not expected to use?")
    

    def set_chalk(self, drawing: bool):
        """sets the chalk to either be drawing or not drawing"""
        if drawing == this.drawing:
            return #can skip if same state.
        this.drawing = drawing



