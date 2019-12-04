"""
Servo control functions for Pi
Author Jonas Hurlen
Version 1.0
Date: Dec 2, 2019

"""

import RPi.GPIO as GPIO
import math
from time import sleep
dc = 0

#storage value for the current angle of the motor
_anglePosition = 90
"""
Initializes the GPIO for the motor
"""
def motorInit:
    #Pin 11 set up for GPIO control
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11,GPIO.OUT)
    
    pwm = GPIO.PWM(11,50)
    pwm.start(dc)

"""
Function for taking a radian angle and setting the servo motor to that angle
"""
def setAngle(angle):
    global _anglePosition
    _anglePosition = angle
    #Rad to deg conversion
    angle = angle * (180/math.pi)
    duty = angle / 18 + 2
    
    GPIO.output(11, True)
    pwm.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(11,False)
    pwm.ChangeDutyCycle(0)
    
"""
Provides a simple reset to the system to 90 degrees
"""
def reset():
    setAngle(math.pi/2)
    global _anglePosition
    _anglePosition = math.pi/2

"""
Steady incremental pan of the servo 
"""
def pan(current, increment):
    if increment > 0:
        angle = current + 180/math.pi
    else:
        angle = current - 180/math.pi
    setAngle(angle)
    global _anglePosition
    _anglePosition = angle
    return (angle)
    
"""
Returbs the last angle sent to the motor
"""
def getAngle():
    return(_anglePosition)

"""
Stops GPIO communications
"""
def endComms():
    pwm.stop()
    GPIO.cleanup()