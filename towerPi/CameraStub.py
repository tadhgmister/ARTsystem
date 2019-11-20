import random

class Camera:
    def __init__(self):
        i = 0

    def takePhoto(self):
        LEDLctions = []

        for i in range(0,4):
            x = random.uniform(22, 624)
            y = random.uniform(22, 624)
            LEDLctions.append([x,y])

        if len(LEDLctions) > 4:
            print('SUDO ERROR')
        return LEDLctions