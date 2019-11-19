"""
Contains code to turn sequence of coordinates into sequence of movement commands
"""
from matplotlib import pyplot
import math
import itertools
from typing import Generator, Iterator, Tuple
from common import Position, MOVE
from vehicleController import Controller as Vehicle
import towerCommunication

def pol_dist(dx,dy):
    """converts (x,y) distance to polar distance (straight line distance)"""
    return abs(dx + 1j*dy) #abs on complex numbers is designed to do this.

def move_to_point(curPos: Position, targetX: float, targetY: float) -> Generator[MOVE,None,None]:
    """generates sequence of movement commands to form strait-ish path
    towards target, based on resolution do not expect this to get exactly
    to the target, this will try to get as close as possible

    ignores the facing direction of target position"""
    (curx, cury, curfacing) = (curPos.x, curPos.y, curPos.facing)
    (tarx, tary) = (targetX, targetY)
    ### Orient the correct direction
    needed_facing = math.atan2(tary - cury, tarx - curx)
    #TODO: SHOULD CONSIDER WRAP AROUND FOR ANGLES, WON'T TURN OPTIMAL DIRECTION THIS WAY
    steps_to_turn = (needed_facing - curfacing) // Vehicle.WHEEL_TURN_INCREMENT
    dir_to_turn = MOVE.R if steps_to_turn < 0 else MOVE.L
    yield from itertools.repeat(dir_to_turn, int(abs(steps_to_turn)))
    curfacing += steps_to_turn * Vehicle.WHEEL_TURN_INCREMENT

    #we are now within one turn increment from the direction we need to move
    #TODO: do zig-zagging so that car tries to stay roughly on the line
    steps_to_move = pol_dist(tarx-curx, tary-cury) // Vehicle.WHEEL_STEP_INCREMENT
    yield from itertools.repeat(MOVE.F, int(steps_to_move))

def move_along_line(controller: Vehicle, iter_pos: Iterator[Tuple[int,Tuple[float,float]]]):
    """
    moves car along the line
    This works by 
    """
    for step, (tarx, tary) in iter_pos:
        for instruction in move_to_point(controller.position, tarx, tary):
            controller.move(instruction)
            yield controller.position


############# TEST CODE 

def collect_test_positions(lines_of_drawing):
    def positionToTuple(pos: Position):
        return (pos.x, pos.y)
    NaN = float("nan")
    controller = Vehicle()
    controller.correct_actual_position(None)
    for (lineid, line) in lines_of_drawing:
        yield map(positionToTuple, move_along_line(controller, line))

if __name__ == "__main__":
    print("MANUAL TEST")
    lines = towerCommunication.get_lines_of_drawing(0)
    for idx,shape in enumerate(collect_test_positions(lines)):
        [x,y] = zip(*shape)
        
        pyplot.plot(x,y, label=f"shape{idx}")
    # need to get new iterator since other one is exausted.
    lines = towerCommunication.get_lines_of_drawing(0)
    for (lineID, line) in lines:
        [x,y] = zip(*map(lambda x:x[1], line))
        pyplot.plot(x,y, label="actual")
    pyplot.title("sample output")
    pyplot.legend()
    pyplot.show()
