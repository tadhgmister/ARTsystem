"""
SYSC3010 Fall 2019, Group W6

This code is responsible for communicating with the Arduino on the vehicle in
our system.  The serial port path should be set up manually to avoid sending
data to the wrong serial port.

Version 1.1: Updated running loop and set default serial port path to ttyUSB0

Author: Scott Malonda
Version: 1.1
Date: Nov 16, 2019
"""

import serial

running = True
waiting = False
readyToMove = True
received = 0
toSend = 0

arduino = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600
    )
if arduino.isOpen():
    arduino.close()
arduino.open()
arduino.isOpen()

print("Input some movement instruction values in the format '49 50 21'.\n" +
      "49, 51, and 52 (ASCII 0, 2, and 3) are the only expected values.")
while running:
    if readyToMove:
        text = input(">>> ")
        if (text == "stop" or text == "Stop"):
            running = False
            break
    
        # Parsing the command line arguments
        nums = text.split(" ")
        toSend = []
        for i in range(0, len(nums)):
            toSend.append(int(nums[i]))
        

        # Sends the instructions that were inputted and waits to receive a message
        # back from the Arduino
        arduino.write(bytearray(toSend))
        readyToMove = False
        waiting = True

    # Checks if the Arduino has sent us a message   
    while waiting:
        if(arduino.in_waiting > 0):
            line = arduino.readline()
            print(line)
            array = bytearray(line)
            if(array[0] == 6):
                readyToMove = True
                waiting = False

