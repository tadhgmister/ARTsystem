try:
    from ImgProcessing import ImgProc
except ImportError:
    from .ImgProcessing import ImgProc

import cv2
import matplotlib.pyplot as plt


cameraSensor = ImgProc(1)

# f = '5x5 for basic edges.jpg'
# f = 'w6.jpg'
# cameraSensor.makePattern(f)

x = 25.0
y = 600.0
o = 3.141592653 / 2
LEDXcoords, LEDYcoords = cameraSensor.getPos(x,y,o)

gLED = [LEDXcoords['g'], LEDYcoords['g']]
bLED = [LEDXcoords['b'], LEDYcoords['b']]
rLED = [LEDXcoords['rHigh'], LEDYcoords['rHigh']]
# o is for 'origin' LED
oLED = [LEDXcoords['rLow'], LEDYcoords['rLow']]

print(gLED[0],'\t',gLED[1])
print(bLED[0],'\t',bLED[1])
print(rLED[0],'\t',rLED[1])

print(oLED[0],'\t',oLED[1])








#status = cameraSensor.getStatus()

# print(pos)
# print(status)