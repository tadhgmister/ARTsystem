import socket
from common import Position
import towerCommunication

requester = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
pos1 = Position(2, 2, 1.5)
pos2 = Position(3, 5, 2.544)
pos3 = Position(5, 4, 0.998)

print("Position request 1")
position = towerCommunication.sync_position(pos1, 1, requester)
print("x: "+str(position.x)+"\ny: "+str(position.y)+"\nangle: "+str(position.facing))

print("Position request 2")
position = towerCommunication.sync_position(pos2, 2, requester)
print("x: "+str(position.x)+"\ny: "+str(position.y)+"\nangle: "+str(position.facing))

print("Position request 3")
position = towerCommunication.sync_position(pos3, 3, requester)
print("x: "+str(position.x)+"\ny: "+str(position.y)+"\nangle: "+str(position.facing))
