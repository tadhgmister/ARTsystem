try:
    from ImgProcessing import ImgProc
except ImportError:
    from .ImgProcessing import ImgProc

import cv2
import matplotlib.pyplot as plt


cameraSensor = ImgProc(1)

f = '5x5 for basic edges.jpg'
f = 'w6.jpg'
cameraSensor.makePattern(f)

# x = 25.0
# y = 600.0
# o = 3.141592653 / 2
# pos = cameraSensor.getPos(x,y,o)











#status = cameraSensor.getStatus()

# print(pos)
# print(status)