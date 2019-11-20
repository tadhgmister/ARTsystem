import random

class Servo:

    def __init__(self):
        self.angle = 0

        # SET SERVO MOTOR ANGLE TO 0


    def setAngle(self, anglee):
        self.angle = anglee

    def getAngle(self):
        self.angle = random.uniform(0, 3.141592653)
        return self.angle