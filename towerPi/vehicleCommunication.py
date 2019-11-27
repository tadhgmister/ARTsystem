"""
Contains all code to communicate from the Tower to the Vehicle

Author: Scott Malonda
Version: 1.0
Date: Nov 18, 2019
"""

import socket
from ImgProcessing import ImgProc
from databaseStub import dataStub
from towerCommon import OPCODE, Position


def listen(server: socket):
    """
    Receives a udp message and parses the data into a list of ints.
    - server is the socket that will receive the message

    Returns a list of ints and the address (IP, port) of the sending socket
    """
    raw, addr = server.recvfrom(1024)
    data = []
    for i in range(0, len(raw)):
        data.append(int(raw[i]))

    return data, addr


def reply(server: socket, addr, message):
    """
    Sends a response to the client at address addr
    - server is the socket sending the response
    - addr is the address (IP, port) of the client socket
    - message is the bytearray to be sent
    """
    # Created this in case we want to separate some part of the logic from the main loop
    server.sendto(message, addr)

def getPosition(camera: ImgProc, expectedPos: Position, step, database: dataStub):
    """
    Gets the position of the vehicle from the camera in the format (X, Y, Angle)

    Returns the x,y coordinates of the vehicle and its angle from the positive x axis
    """
    position = camera.getPos(expectedPos) # Gets the position from an ImgProc object
    database.log(position, step)
   
    return position


def getNext(database: dataStub, drawingID, step = 0):
    """
    Gets the next position in the drawing pattern from the database
    - drawingID is the ID of the currently tracked drawing
    - step is the stepID of the next step in the drawing

    Returns a string of points in the format "step,lineID,x,y step,lineID,x,y"
    """
    lines = []
    # TODO: add database access to get the drawing info
    # TODO: Figure out what format to use.  Nested lists aren't playing nice
    lines = database.getStep(drawingID, step)
    
    for i in range(0, len(lines)):
        string = str(step)+str(lines[i][0])+","+str(lines[i][1])+","+str(lines[i][2])+" "
            
    return string

def getDrawing(database, imageID):
    # TODO: Implement database access
    # Placeholder function
    return 1


tracking = False
drawingID = 0
# Setting up the UDP server that we're gonna use
serverIP = 'localhost'
serverPort = 1000
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((serverIP, serverPort))
# Creating the camera and database objects
camera = ImgProc()
database = dataStub()

while True:
    # Blocks while listening for a message.  Once received it identifies the request type,
    # takes any required Tower-side actions, and replies to the sender
    data, addr = listen(server)
    
    if(int(data[0])==OPCODE.STANDBY.value):
        tracking = False
        drawingID = 0
        message = bytearray([OPCODE.ACK.value])
        reply(server, addr, message)

    elif(int(data[0])==OPCODE.TRACK.value):
        if(drawingID!=0):
            # Error if already tracking a drawing
            message = bytearray([OPCODE.ERROR.value])+bytearray("Already tracking a drawing".encode())
            reply(server, addr, message)
        else:
            imageID = data[1]
            drawingID = getDrawing(database, imageID)
            tracking = True
            message = bytearray([OPCODE.ACK.value])
            reply(server, addr, message)

    elif(int(data[0])==OPCODE.POSITION.value):
        expectedPos = pickle.loads(data[2:(len(data)-1)])
        step = int(data[1])
        x, y, angle = getPosition(camera, expectedPos, step, database)
        position = Position(x, y, angle)
        message = bytearray(OPCODE.POSITION.value)+bytearray(pickle.dumps(position))
        reply(server, addr, message)

    elif(int(data[0])==OPCODE.NEXTPOS.value):
        if not(tracking):
            # Error if not tracking a drawing
            message = bytearray(OPCODE.ERROR.value)+bytearray("No active drawing".encode())
            reply(server, addr, message)
        else:
            lines = getNext(database, data[1], data[2])
            message = bytearray(OPCODE.NEXTPOS.value)+bytearray(lines.encode())
            reply(server, addr, message)

    # Clearing variable to avoid reusing data from the last message (redundant)
    data = None
    addr = None
