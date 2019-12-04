"""
main program to run the vehicle pi
the drawing id is passed via command line arguments, this will load drawing info from database and command arduino to move etc.
"""

from . import draw
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("drawing_id", type=int, help="the drawing id from database to draw")

args = parser.parse_args()

draw(args.drawing_id)