import random
class ImgProc:

    def __init__(self):
        self.status = 'standby'

    # returns the camera calculated position of the car
    # FOR TEST it returns a random location between 22cm and 624cm, and orientation between 0 and 3.14rad
    def getPos(self):
        self.status = 'processing'

        # SUDO get from camera:
        x = random.uniform(22, 624)
        y = random.uniform(22, 624)
        orientation = random.uniform(0, 3.141592653)

        self.status = 'standby'
        return [x, y, orientation]

    # if any class wants to know what state the camera is in,
    # this class will give it
    def getStatus(self):
        return self.status