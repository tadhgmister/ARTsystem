"""
Contains all code to communicate from the Tower to the Vehicle

Author: Scott Malonda
Version: 1.0
Date: Nov 18, 2019
"""

import socket
from ImgProcessing import ImgProc
from databaseStub import dataStub
from towerCommon import OPCODE


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
    - message is the list of ints to be sent
    """
    # Created this in case we want to separate some part of the logic from the main loop
    server.sendto(bytearray(message), addr)


def getPosition(camera):
    """
    Gets the position of the vehicle in the format (X, Y, Angle)

    Returns the x,y coordinates of the vehicle and its angle from the positive x axis
    """
    # TODO: Add log() fuction
    # Contact the camera to get the current position.
    position = camera.getPos() # Gets the position from an ImgProc object
    database.log()
   
    return position


def getNext(database, drawingID, step = 0):
    """
    Gets the next position in the drawing pattern from the database
    - drawingID is the ID of the currently tracked drawing
    - step is the stepID of the next step in the drawing

    Returns a nested list of points in the format [step, lineID, [x,y]]
    """
    lines = []
    # TODO: add database access to get the drawing info
    # Figure out what format to use.  Nested lists aren't playing nice
    return lines


tracking = False
drawingID = 0
# Setting up the UDP server that we're gonna use
serverIP = 'localhost'
serverPort = 1000
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((serverIP, serverPort))
# Creating the camera and database objects
cameraSensor = ImgProc()
database = dataStub()

while True:
    # Blocks while listening for a message.  Once received it identifies the request type,
    # takes any required Tower-side actions, and replies to the sender
    data, addr = listen(server)
    
    if(data[0]==STANDBY):
        tracking = False
        drawingID = 0
        message = [ACK]
        reply(server, addr, message)

    elif(data[0]==TRACK):
        if(drawingID==0):
            message = [ERROR, "Already tracking a drawing"]
            reply(server, addr, message)
        else:
            imageID = data[1]
            drawingID = getDrawing(imageID)
            tracking = True
            # TODO: send a message to the camera to turn on?
            message = [ACK]
            reply(server, addr, message)

    elif(data[0]==POSITION):
        # If the request has a step number, pass it as an argument to getPosition()
        x, y, angle = getPosition()
        message = [POSITION, x, y, angle]
        reply(server, addr, message)

    elif(data[0]==NEXTPOS):
        if not(data[1]==drawingID):
            message = [ERROR, "drawingID does not match tracked drawing"]
            reply(server, addr, message)
        lines = getNext(database, data[1], data[2])
        message = [NEXTPOS, lines]

    # Clearing variable to avoid reusing data from the last message (redundant)
    data = None
    addr = None
