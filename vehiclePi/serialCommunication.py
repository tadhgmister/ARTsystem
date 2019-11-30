"""
SYSC3010 Fall 2019, Group W6

This code is responsible for communicating with the Arduino on the vehicle in
our system.  The serial port path should be set up manually to avoid sending
data to the wrong serial port.

Version 1.1: Updated running loop and set default serial port path to ttyUSB0
Version 1.2: Moved code into a function for use by other scripts.

Author: Scott Malonda
Version: 1.1
Date: Nov 16, 2019
"""

import serial
from common import MOVE

def send_moves(arduinoPort = '/dev/ttyUSB0', *moves):
    """
    Sends a list of movement instructions to the vehicle Arduino via USB serial
    connection.
    
    Function assumes that the vehicle is ready to move when it is called, and
    blocks until it receive a ready-to-move signal from the Arduino after the
    instructions are set.
    """
    arduino = serial.Serial(
        port=arduinoPort,
        baudrate=9600
        )
    if arduino.isOpen():
        arduino.close()
    arduino.open()

    waiting = False
    received = 0
    toSend = []
    
    # Parsing the moves argument
    for i in range(0, len(moves)):
        if (moves[i]==MOVE.F) toSend.append(48)
        elif (moves[i]==MOVE.B) toSend.append(49)
        elif (moves[i]==MOVE.R) toSend.append(50)
        elif (moves[i]==MOVE.L) toSend.append(51)
        elif (moves[i]==MOVE.FL) toSend.append(52)
        elif (moves[i]==MOVE.FR) toSend.append(53)
        elif (moves[i]==MOVE.BL) toSend.append(54)
        elif (moves[i]==MOVE.BR) toSend.append(55)
        

    # Sends the instructions that were inputted and waits to receive a message
    # back from the Arduino
    arduino.write(bytearray(toSend))
    waiting = True

    # Checks if the Arduino has sent us a message   
    while waiting:
        if(arduino.in_waiting > 0):
            line = arduino.readline()
            print(line)
            array = bytearray(line)
            if(array[0] == 6):
                waiting = False

