

def draw(drawing_id, initial_position = None):
    # structurally it would make way more sense to put the draw function in it's own file, but putting it in __init__ is easier
    # but for the sake of keeping the top level namespace clean we will do imports needed for draw inside
    # idk why I'm doing this, I could just add another file and define draw there....
    from .vehicleController import Controller
    from .common import Position
    from .pathFinding import move_along_line
    from .towerCommunication import get_lines_of_drawing

    print("DRAWING", drawing_id)

    vehicle = Controller(initial_position)
    if initial_position is None:
        # we assume car is initially placed at 90deg relative to the camera, so give initial position that makes the camera point there.
        vehicle.position = Position(0,1)
        vehicle.correct_actual_position(None)

    lines_iter = get_lines_of_drawing(drawing_id)

    for line_id, points_iter in lines_iter:
        print("on line", line_id)
        move_along_line(vehicle, points_iter)
        #TODO: do additional correction here?