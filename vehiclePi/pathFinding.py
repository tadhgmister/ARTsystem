"""
Contains code to turn sequence of coordinates into sequence of movement commands
"""
from matplotlib import pyplot
from matplotlib import animation
import math
import itertools
from typing import Generator, Iterator, Tuple
try:
    from common import Position, MOVE
    from vehicleController import Controller as Vehicle
    import towerCommunication
except ImportError:
    from .common import Position, MOVE
    from .vehicleController import Controller as Vehicle
    from . import towerCommunication

# set to true below in if __name__ == "__main__"
DEBUG = False
W = 20.2
H = 10.2
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
    steps_to_move = pol_dist(tarx-curx, tary-cury) // Vehicle.WHEEL_STEP_INCREMENT
    if steps_to_move == 0:
        return
    ### Orient the correct direction
    needed_facing = math.atan2(tary - cury, tarx - curx)
    #TODO: SHOULD CONSIDER WRAP AROUND FOR ANGLES, WON'T TURN OPTIMAL DIRECTION THIS WAY
    angle_to_turn = (needed_facing - curfacing) % (2*math.pi)
    if angle_to_turn > math.pi:
        #should be turning left instead. subtract 2pi radians to be a negative number
        angle_to_turn -= 2*math.pi
    steps_to_turn = angle_to_turn // Vehicle.WHEEL_TURN_INCREMENT
    dir_to_turn = MOVE.R if steps_to_turn < 0 else MOVE.L
    yield from itertools.repeat(dir_to_turn, int(abs(steps_to_turn)))
    curfacing += steps_to_turn * Vehicle.WHEEL_TURN_INCREMENT

    #we are now within one turn increment from the direction we need to move
    #TODO: do zig-zagging so that car tries to stay roughly on the line
    #steps_to_move = pol_dist(tarx-curx, tary-cury) // Vehicle.WHEEL_STEP_INCREMENT
    yield from itertools.repeat(MOVE.F, int(steps_to_move))

    #yield MOVE.L

def move_along_line(controller: Vehicle, iter_pos: Iterator[Tuple[int,Tuple[float,float]]]):
    """moves car along the line"""
    # TODO: we should check if there are no movement instructions to get to
    # first point and skip the chalk_up then chalk_Down in that case.
    yield MOVE.CHALK_UP
    got_to_first_point = False
    for step, (tarx, tary) in iter_pos:
        for instruction in move_to_point(controller.position, tarx, tary):
            controller.move(instruction)
            yield instruction
        if not got_to_first_point:
            got_to_first_point = True
            yield MOVE.CHALK_DOWN
        if DEBUG:
            global deviation
            deviation = max(deviation, pol_dist(controller.position.x - tarx,
                                               controller.position.y - tary))
    
                


############# TEST CODE 

def collect_test_positions(lines_of_drawing):
    def positionToTuple(pos: Position):
        return (pos.x, pos.y)
    NaN = float("nan")
    controller = Vehicle(Position(0,0))
    #controller.correct_actual_position(None)
    all_paths = []
    path = []
    drawing = True
    for (lineid, line) in lines_of_drawing:
        # we ignore the instruction in the loop here, just after each iteration we just read the controller's position.
        for inst in move_along_line(controller, line):
            if inst is MOVE.CHALK_UP:
                # end of line, yield it and start a new one
                drawing = False
                if path:
                    all_paths.append(path)
                path = []
            elif inst is MOVE.CHALK_DOWN:
                drawing = True
            elif drawing:
                path.append((controller.position.x, controller.position.y))
            yield
            animate_frame(all_paths, path, controller.position)
    
    while True:
        yield
        animate_frame(all_paths, path, controller.position)

def animate_frame(finished_paths, current_path, pos: Position):
    pyplot.clf()
    pyplot.xlim((-5, W+5))
    pyplot.ylim((-5, H+5))
    pyplot.scatter([pos.x], [pos.y])
    pyplot.plot([pos.x, pos.moved_forward(3).x], [pos.y, pos.moved_forward(3).y])
    for idx,path in enumerate(finished_paths):
        [x,y] = zip(*path)
        pyplot.plot(x,y)
    if current_path:
        [x,y] = zip(*current_path)
        pyplot.plot(x,y)

if __name__ == "__main__":
    DEBUG = True
    deviation = 0
    tolerance = 2*Vehicle.WHEEL_STEP_INCREMENT #mm allowed deviation
    print("RUNNING TEST")
    lines = towerCommunication.get_lines_of_drawing(2)

    ### haha lol, I accidentally totally changed the format of collect_test_positions so this test code is completely broken, oops.
    ### oh well, the 
    # for idx,path in enumerate(collect_test_positions(lines)):
        
    #     [x,y] = zip(*path)
        
    #     pyplot.plot(x,y, label=f"shape{idx}")
    # print(f"max deviation: {deviation:.3f}mm")
    # if deviation > tolerance:
    #     import sys
    #     print(f"FAIL: algorithm results in {deviation/Vehicle.WHEEL_STEP_INCREMENT:.1%} of the step increment", file=sys.stderr)
    # # need to get new iterator since other one is exausted.
    # lines = towerCommunication.get_lines_of_drawing(1)
    # for (lineID, line) in lines:
    #     [x,y] = zip(*map(lambda x:x[1], line))
    #     pyplot.plot(x,y, label="actual")
    # pyplot.title("sample output")
    # pyplot.legend()
    # pyplot.show()
    it = collect_test_positions(lines)
    def next_frame(i=None):
        try:
            next(it)
        except StopIteration:
            pass
    ani = animation.FuncAnimation(pyplot.gcf(), next_frame, 1)
    
    pyplot.show()


