# Test script for the serial communication

import serialCommunication
import itertools

#text = input("Type the port name (ex. /dev/ttyUSB0)\n>>> ")
test1 = [48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48]
mapping = {"w":48, "a":50, "d": 51, "s":49}
def get_input():
    return input("enter: ")
print("Running manual test...")
for inp in iter(get_input, ''):
    command = [mapping[c] for c in inp]
    print(command)
    serialCommunication.send_moves('/dev/ttyUSB0', command)
    
print("Running automated test...")
serialCommunication.send_moves('/dev/ttyUSB0', test1)
    