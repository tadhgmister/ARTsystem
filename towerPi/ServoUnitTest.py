# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 16:39:26 2019

@author: Jonas

Servo Test Driver for ART System
"""


public class servoTest{
        import RPi.GPIO as GPIO
        from time import sleep
        dc = 0 #initial duty cycle


        #Pin 11 Control Pin
        GPIO.setup(11,GPIO.OUT)
        PWMPin = GPIO.PWM(11,50)
        PWMPin.start(dc)
        
        
        def SetAngle(angle):
            duty = angle / 18 + 2
            GPIO.output(11, True)
            pwm.ChangeDutyCycle(duty)
            sleep(1)
            GPIO.output(11, False)
            pwm.ChangeDutyCycle(0)
            
            
        public void reset(){
                SetAngle(90)
                }
        
        public void rangeTest(){
                SetAngle(0)
                time.sleep(0.5)
                SetAngle(180)
                
                }
        
        public void increments(init, complete){
                currAngle = init
                while(currAngle < complete){
                        SetAngle(currAngle)
                        currAngle++
                        }
                }
        
        pwm.stop()
        GPIO.cleanup()
        
        }
