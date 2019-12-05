"""
Contains all code to communicate from vehicle to tower

Version 1.1: Added socket methods and a placeholder server address for communicating with
    the tower.  Sync_position now returns the real position; calculated_position is ignored.
Version 1.2: Updated sync_position() to send and expect a pickled tuple in the UDP request and
    reply respectively.
"""
import sqlite3
import itertools
import socket
import pickle
try:
    from common import Position, OPCODE
except ImportError:
    from .common import Position, OPCODE

from typing import Generator, Tuple, Iterator

server_address = ('192.168.2.2', 10000)
    
def sync_position(calculated_position: Position, current_step: int, client: socket.socket) -> Position:
    """asks tower to calculate exact position of the vehicle
    also sends the current step and calculated position to sync info
    this will block execution until tower can take and process image of vehicle
    so it may take long time.

    calculated position or current_step may be None if not calling this in middle of drawing

    Returns position given by the tower
    """
    if calculated_position is None:
        # can just say car is exactly at tower, not realistic but reasonable for testing.
        calculated_position = Position(0,0)

    # Position request is a tuple containing (opcode, step, Position)
    message = pickle.dumps((OPCODE.POSITION.value, current_step, calculated_position))
    client.sendto(message, server_address)
    client.settimeout(2)
    raw, server = client.recvfrom(1024)
    data = pickle.loads(raw)
    # Position packets are a tuple containing (opcode, Position)
    if not(int(data[0])==OPCODE.POSITION.value):
        raise TypeError("Error: Received unexpected packet type {!r}".format(data[0]))

    real_position = data[1]

    return real_position 

def get_lines_of_drawing(drawing_ID, step_ID=None):
    #-> Generator[Tuple[int,Iterator[Tuple[int,Tuple[float,float]]]],None,None]:
    """generates a sequence of iterators in the following manner:
    for line_num, line_iter in get_lines_of_drawing(0):
        for step, (x,y) in line_iter:
            do_stuff(x,y)

    - line_num is the line number stored in database, it will increment sequentially from 0 for each drawing
    - line is iterator to be used in nested loop
    - step is step_ID stored in database, these don't reset to 0 for each line
       if the car does additional interpolation to get a higher resolution of points the step might repeat
       for a few sequential points.

    If step_ID is not given this will start from last recorded step in drawing.
    """
    def key(item: ("step", "line", "point")):
        return item[1]
    def remove_line(item: ("step", "line", "point")):
        [step, line, point] = item
        return (step, point)
    iterator = itertools.groupby(load_points_for_drawing(drawing_ID, step_ID), key)

    for line_id, line_iter in iterator:
        yield (line_id, map(remove_line, line_iter))
    
    
def load_points_for_drawing_LOCAL_DB(drawing_ID, step_ID=None):
    """loads points from the tower and returns them as a generator
    points are yielded in a tuple (ID,line, x,y) where
    - ID is the step_ID stored in the database
    - line is the line id in the database
    - x,y are coordinates in mm relative to the tower.
   
    if step_ID is not given this will load the current step from the drawing table and start from there
    to start at the beginning you can pass step_ID=0
    """
    from databaseHelper import db as database
    drawingInfo = database.load_drawing_info(drawing_ID)
    patternInfo = database.load_pattern_info(drawingInfo.patternUsed)
    Xscale = (drawingInfo.bound2x - drawingInfo.bound1x)/patternInfo.width
    Yscale = (drawingInfo.bound2y - drawingInfo.bound1y)/ patternInfo.height
    xmin = drawingInfo.bound1x
    ymin = drawingInfo.bound1y
    for step in database.load_steps_for_pattern(drawingInfo.patternUsed):
        x = xmin + step.x * Xscale
        y = ymin + step.y * Yscale
        yield (step.stepIndex, step.lineIndex, x,y)
        
load_points_for_drawing = load_points_for_drawing_LOCAL_DB
############################## TEST CODE

def load_points_for_drawing_MOCK(drawing_ID, step_ID=None):
    """
    Loads a hard coded set of points to test with.
    Points are in the form of several squares offset from each other.
    """
    if drawing_ID != 1:
        raise ValueError(f"cannot find a drawing with drawing ID {drawing_ID}")
    BOX_WIDTH, BOX_HEIGHT = 10,10 #mm
    OFFSET_X, OFFSET_Y = 20,20
    NUM_BOXES = 3
    points = [(0,0), (0, BOX_HEIGHT), (BOX_WIDTH, BOX_HEIGHT), (BOX_WIDTH, 0), (0, 0)]
    # 3 boxes offset with full line and point ids set.
    # in format of (stepID, lineID, (x,y))
    all_steps = [(idx+line*len(points),
                line,
                x+line*OFFSET_X, y+line*OFFSET_Y)
                    for line in range(NUM_BOXES)
                        for idx, (x,y) in enumerate(points)]
    if step_ID is None:
        step_ID = 0 #no stepID was given so start at beginning.
    if not isinstance(step_ID, int):
        raise TypeError(f"step should be an integer, got {type(step_ID)}")
    if not(0 <= step_ID < len(all_steps)):
        raise IndexError(f"drawing {drawing_ID} does not contain a step {step_ID}")
    #otherwise yield all remaining steps.
    yield from all_steps[step_ID:]

try:
    mydb = sqlite3.connect("./testDB.db")
    test = list(load_points_for_drawing(1))
except Exception:
    load_points_for_drawing = load_points_for_drawing_MOCK
    print("ERROR: couldn't connect to database, using mock function to load data")
    import traceback
    traceback.print_exc()
    mydb = None

def get_lines_of_drawing(drawing_ID, step_ID=None) -> (
    Generator[Tuple[int,Iterator[Tuple[int,Tuple[float,float]]]],None,None]):
    """generates a sequence of iterators in the following manner:
    for line_num, line_iter in get_lines_of_drawing(0):
        for step, (x,y) in line_iter:
            do_stuff(x,y)

    - line_num is the line number stored in database, it will increment sequentially from 0 for each drawing
    - line is iterator to be used in nested loop
    - step is step_ID stored in database, these don't reset to 0 for each line
       if the car does additional interpolation to get a higher resolution of points the step might repeat
       for a few sequential points.

    If step_ID is not given this will start from last recorded step in drawing.
    """
    
    def key(item: ("step", "line", "point")):
        return item[1]
    def remove_line(item: ("step", "line", "x", "y")):
        return (item[0], (item[2], item[3]))
    iterator = itertools.groupby(load_points_for_drawing(drawing_ID, step_ID), key)

    for line_id, line_iter in iterator:
        yield (line_id, map(remove_line, line_iter))
    
    


if __name__ == "__main__":
    print("RUNNING MANUAL TEST CASES", end="\n\n")

    print("LOADING LINES LOOP")
    for line_id, line in get_lines_of_drawing(1):
        print(f"---- on line {line_id}")
        for step, (x,y) in line:
            print(f"step {step}: ({x}, {y})")
    if mydb:
        mydb.close()
