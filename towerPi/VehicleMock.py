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
server_address = ('localhost', 1000)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def checkPos(testNum):
    """
    Sends a checkPosition request to the Tower and waits for a response
    Prints the result of the test request
    """
    message = [OPCODE.POSITION.value]
    client.sendto(bytearray(message), server_address)
    
    raw, server = client.recvfrom(4096)
    data = raw.decode().split(" ")
    if(int(data[0])==OPCODE.POSITION.value):
        print('Test ' +str(testNum)+ ' Position request: Received {!r}.  '
              .format(OPCODE.POSITION)+'Please manually verify values:')
        print(data)
    else:
        print('Test ' +str(testNum)+ ' Position request: Failed.  Received: {!r}'
              .format(data))


def track(testNum, imgID, expected):
    """
    Sends a track request to the Tower and waits for a response
    Prints the result of the test request
    """
    message = [OPCODE.TRACK.value, imgID]
    client.sendto(bytearray(message), server_address)

    data, server = client.recvfrom(4096)
    if(data[0]==expected.value):
        print('Test ' +str(testNum)+ ' Track request: Passed.  Received {!r}'
              .format(expected))
    else:
        print('Test ' +str(testNum)+ ' Track request: Failed.  Received OpCode:'+
              ' {!r}'.format(data)+'\nExpected OpCode: '+str(expected.value))


def getNextStep(testNum, imgID, stepID, expected):
    """
    Sends a getLines request to the Tower and waits for a response
    Prints the result of the test request
    """
    message = [OPCODE.NEXTPOS.value, imgID, stepID]
    client.sendto(bytearray(message), server_address)
    
    raw, server = client.recvfrom(4096)
    data = raw.decode().split(" ")
    if(int(data[0])==expected.value):
        print('Test ' +str(testNum)+ ' Next Step request: Received {!r}.  '
              .format(expected)+'Please manually verify values:')
        print(data)
    else:
        print('Test ' +str(testNum)+ ' Position request: Failed.  Received OpCode:'+
              ' {!r}'.format(data)+'\nExpected OpCode: '+str(expected.value))


def standby(testNum):
    """
    Sends a standby request to the Tower and waits for a response.
    Prints the result of the test request
    """
    message = [OPCODE.STANDBY.value]
    client.sendto(bytearray(message), server_address)

    data, server = client.recvfrom(4096)
    if(data[0]==OPCODE.ACK.value):
        print('Test ' +str(testNum)+ ' Standby request: Passed.  Received {!r}'.format(OPCODE.ACK))
    else:
        print('Test ' +str(testNum)+ ' Standby request: Failed.  Received: {!r}'.format(data))
    
if __name__ == "__main__":
    """
    Sends several "Check Position" requests while also changing the state of
    the server (starting tracking, switching to standby)
    """
    print("Running automated tests...\n")

    checkPos(1)  # Check position while not tracking
    track(2, 1, OPCODE.ACK) # Start tracking
    track(3, 2, OPCODE.ERROR) # Attempt to track a different drawing
    checkPos(4) # Check position while tracking
    getNextStep(5, 1, 1, OPCODE.NEXTPOS)
    standby(6)  # Standby while tracking
    getNextStep(7, 1, 1, OPCODE.ERROR)
    standby(8)  # Standby while not tracking

    print("\nDone automated tests.  Closing UDP socket.")
    client.close()
    print("Enter anything to quit execution.")
    input(">>> ")   # Gives you time to review the tests before quitting execution

