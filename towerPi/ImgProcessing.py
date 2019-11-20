try:
    from CameraStub import Camera
except ImportError:
    from .CameraStub import Camera

try:
    from ServoStub import Servo
except ImportError:
    from .ServoStub import Servo

import random

class ImgProc:

    def __init__(self):
        self.status = 'standby'
        self.servo = Servo()
        self.camera = Camera()


    # returns the camera calculated position of the car
    # FOR TEST it returns a random location between 22cm and 624cm, and orientation between 0 and 3.14rad
    def getPos(self):
        self.status = 'processing'

        LEDs = self.camera.takePhoto()

        # SUDO get from camera:
        orientation = self.servo.getAngle()
        x, y = LEDs[0]
        self.status = 'standby'
        return [x, y, orientation]

    # if any class wants to know what state the camera is in,
    # this class will give it
    def getStatus(self):
        return self.status