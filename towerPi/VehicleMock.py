"""
SYSC3010 Group W6, Fall 2019

Code to mock the vehicle of our system and send requests to the Tower for
integration testing.

Author: Scott Malonda
Version: 1.0
Date: Nov 16, 2019
"""

import socket
import time
from towerCommon import OPCODE

# Setting up the client socket and declaring the server info
server_address = ('localhost', 10000)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(('localhost', 9999))

POSITION = 3
STANDBY = 0
TRACK = 2

def checkPos(testNum):
    """
    Sends a checkPosition request to the Tower and waits for a response
    Prints the result of the test request
    """
    message = [POSITION]
    print("Sending position request: " +str(message))
    client.sendto(bytearray(message), server_address)
    
    data, server = client.recvfrom(4096)
    if(output[0]==POSITION):
        print('Test ' +str(testNum)+ ' CheckPos request: Received position response.  Please manually verify values')
        print(data)
    else:
        print('Test ' +str(testNum)+ ' CheckPos request: Failed.  Received: {!r}'.format(data))


def track(testNum, ID, expected):
    """
    Sends a track request to the Tower and waits for a response
    Prints the result of the test request
    """
    message = [TRACK, ID]
    print("Sending track request: " +str(message))
    client.sendto(bytearray(message), server_address)

    data, server = client.recvfrom(4096)
    if(data[0]==expected):
        print('Test ' +str(testNum)+ ' Track request: Passed.  Received packet: {!r}'.format(data))
    else:
        print('Test ' +str(testNum)+ ' Track request: Failed.  Received: {!r}'.format(data))


def standby(testNum):
    """
    Sends a standby request to the Tower and waits for a response.
    Prints the result of the test request
    """
    message = [STANDBY]
    client.sendto(bytearray(message), server_address)

    data, server = client.recvfrom(4096)
    if(data[0]==ACK):
        print('Test ' +str(testNum)+ ' Standby request: Passed.  Received Ack packet')
    else:
        print('Test ' +str(testNum)+ ' Standby request: Failed.  Received: {!r}'.format(data))
    
if __name__ == "__main__":
    """
    Sends several "Check Position" requests while also changing the state of
    the server (starting tracking, switching to standby)
    """
    print("Running automated tests...")

    checkPos(1)  # Check position while not tracking
    track(2, 1, ACK) # Start tracking
    track(3, 2, ERROR) # Attempt to track a different drawing
    checkPos(4) # Check position while tracking
    standby(5)  # Standby while tracking
    standby(6)  # Standby while not tracking

    print("Done automated tests.  Closing UDP socket.")
    client.close()
    print("Enter anything to quit execution.")
    input(">>> ")   # Gives you time to review the tests before quitting execution

