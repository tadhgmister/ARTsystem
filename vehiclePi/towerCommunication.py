"""
Contains all code to communicate from vehicle to tower

Version 1.1: Added socket methods and a placeholder server address for communicating with
    the tower.  Sync_position now returns the real position; calculated_position is ignored.
"""
import itertools
import socket
from common import Position, OPCODE



server_address = ('localhost', 1000)
    
def sync_position(calculated_position: Position, current_step: int, client: Socket) -> Position:
    """asks tower to calculate exact position of the vehicle
    also sends the current step and calculated position to sync info
    this will block execution until tower can take and process image of vehicle
    so it may take long time.

    calculated position or current_step may be None if not calling this in middle of drawing

    Returns position given by the tower
    """
    message = [OPCODE.POSITION.value]   # CheckPos message.  Only the OpCode is required
    client.sendto(bytearray(message), server_address)

    raw, server = client.recvfrom(1024)
    data = raw.decode().split(" ")  # Position packets are a byte array of string data containing [opcode,x,y,facing]
    if not(int(data[0])==OPCODE.POSITION.value):
        raise TypeError(f"Unexpected error: Received unexpected packet type {!r}".format(data[0]))

    real_position = Position(float(data[1]), float(data[2]), float(data[3]))

    #TODO: Calculate error using calculated_position and real_position?
    if calculated_position is None:
        # can just say car is exactly at tower, not realistic but reasonable for testing.
        calculated_position = Position(0,0)
    return real_position 


def load_points_for_drawing(drawing_ID, step_ID=None):
    """loads points from the tower and returns them as a generator
    points are yielded in a nested tuple (ID,line, (x,y)) where
    - ID is the step_ID stored in the database
    - line is the line id in the database
    - x,y are coordinates in mm relative to the tower.
   
    if step_ID is not given this will load the current step from the drawing table and start from there
    to start at the beginning you can pass step_ID=0
    """
    # TODO: do actual loading
    return load_points_for_drawing_MOCK(drawing_ID, step_ID)

def load_points_for_drawing_MOCK(drawing_ID, step_ID=None):
    if drawing_ID != 0:
        raise ValueError(f"cannot find a drawing with drawing ID {drawing_ID}")
    BOX_WIDTH, BOX_HEIGHT = 10,10 #mm
    OFFSET_X, OFFSET_Y = 20,20
    NUM_BOXES = 3
    points = [(0,0), (0, BOX_HEIGHT), (BOX_WIDTH, BOX_HEIGHT), (BOX_WIDTH, 0), (0, 0)]
    # 3 boxes offset with full line and point ids set.
    all_steps = [(idx+line*len(points),
                line,
                (x+line*OFFSET_X, y+line*OFFSET_Y))
                    for line in range(NUM_BOXES)
                        for idx, (x,y) in enumerate(points)]
    if step_ID is None:
        step_ID = 0
    if not isinstance(step_ID, int):
        raise TypeError(f"step should be an integer, got {type(step_ID)}")
    if not(0<=step_ID < len(all_steps)):
        raise IndexError(f"drawing {drawing_ID} does not contain a step {step_ID}")
    
    yield from all_steps[step_ID:]


def get_lines_of_drawing(drawing_ID, step_ID=None)
     -> Generator[Tuple[int,Iterator[Tuple[int,Tuple[float,float]]]],None,None]:
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
    # FOR FUTURE USE
    # TODO: un-comment the code and properly parse the packet for step data
    # Request the next lines in the drawing from the Tower
    #message = [OPCODE.NEXTPOS.value, drawing_ID, step_ID]
    #client.sendto(bytearray(message), server_address)
    #
    #raw, server = client.recvfrom(1024)
    #data = raw.decode().split(" ")
    # Checking if the packet is an error/unexpected packet
    #if(int(data[0])==OPCODE.ERROR.value):
    #    raise TypeError(f"Tower-side Error: {!r}".format(raw.decode()))
    #elif not(int(data[0])==OPCODE.POSITION.value):
    #    raise TypeError(f"Error: Received unexpected packet type {!r}".format(data[0]))
    
    def key(item: ("step", "line", "point")):
        return item[1]
    def remove_line(item: ("step", "line", "point")):
        return (item[0], item[2])
    iterator = itertools.groupby(load_points_for_drawing(drawing_ID, step_ID), key)

    for line_id, line_iter in iterator:
        yield (line_id, map(remove_line, line_iter))
    
    


if __name__ == "__main__":
    print("RUNNING MANUAL TEST CASES", end="\n\n")

    print("LOADING LINES LOOP")
    for line_id, line in get_lines_of_drawing(0):
        print(f"---- on line {line_id}")
        for step, (x,y) in line:
            print(f"step {step}: ({x}, {y})")

