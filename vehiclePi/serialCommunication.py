# SYSC3010 Fall 2019, Group W6
#
# This code is responsible for communicating with the Arduino on the vehicle in
# our system.  In version 1.0, the serial port path must be set up manually
# before use.  The default is an invalid path.
#
# The Python serial module must be downloaded for this script.
# 
# Author: Scott Malonda
# Version: 1.0
# Date: Nov 14, 2019

import serial

running = True
waiting = False
readyToMove = True
received = 0
toSend = 0

arduino = serial.Serial(
    port='/dev/ttyPort Name',
    baudrate=9600
    )
if arduino.isOpen():
    arduino.close()
arduino.open()
arduino.isOpen()

print("Input some movement instruction values in the format '0 0 0'.  0, 2, " +
      "and 3 are the only expected values")
while running:
    text = input(">>> ")
    if (text == "stop" or text == "Stop"):
        running = False
        break
    
    toSend = int(text.split(" "))
    waiting = True

    # Sends the instructions that were inputted and waits to receive a message
    # back from the Arduino
    while waiting:
        if readyToMove:
            arduino.write(bytearray(toSend))
            readyToMove = False

    # Checks if the Arduino has sent us a message
        if(arduino.in_waiting > 0):
            line = arduino.readline()
            print(line)
            if(line == 1):
                readyToMove = True
                waiting = False

