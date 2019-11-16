"""
SYSC3010 Group W6, Fall 2019

Code to mock the vehicle of our system and send requests to the Tower for
integration testing.

Author: Scott Malonda
Version: 1.0
Date: Nov 16, 2019
"""

import socket

# Setting up the client socket and declaring the server info
server_address = ('localhost', 10000)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

message = [3, 0, 0, 0]
standby = [0]

try:
    """
    Sends several "Check Position" requests while also changing the state of
    the server (starting tracking, switching to standby)
    """
    # TODO: Send more requests and standby/start tracking requests.
    # Currently, this is just sending one request then telling the server to
    # standby.
    
    # Send a request
    print('Sending "Check Position" request to server')
    client.sendto(bytes(message), server_address)

    # Wait for response
    print('Waiting for position...')
    data, server = client.recvfrom(4096)
    print('Received: {!r}'.format(data))

finally:
    print('Telling server to shut down and closing client socket')
    client.sendto(bytes(standby), server_address)
    client.close()
