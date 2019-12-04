/* Code for serial communication between an Arduino and Pi
* Upon receiving a message, the Arduino will activate the motor controls for the instruction,
* wait for a few seconds,
* then send a singe byte serial message saying it's ready for the next message.
* 
* Version 1.1: added switch statement to avoid an avalanche of "if()"s
* Version 1.2: minor updates, initialized readyToMove to 'true' to avoid duplicate 
*   print statements11qqqq
* Version 1.3: Updated Print Commands to be motor commands
* 
* Author:  Scott Malonda & Jonas Hurlen
* Version 1.3
* Date: Nov 16, 2019
*/


#include <Stepper.h>
#include <AccelStepper.h>

#define STEPS 2038

Stepper drawMec(STEPS, 2,4,3,5);
AccelStepper left(AccelStepper::DRIVER , 9,7);
AccelStepper right(AccelStepper::DRIVER , 12,10);

void setup() {

  
}

void loop() {
 forwards();
 //turnRight();
 //turnLeft();
 //backwards();
 delay(100);
}


void up(){
  delay(100);
  drawMec.setSpeed(1);
  drawMec.step(2038/4);

}
void down(){
  delay(100);
  drawMec.setSpeed(1);
  drawMec.step(-2038/4);

}

void forwards(){

  
  left.moveTo(left.currentPosition() + 1000);
  right.moveTo(right.currentPosition() + 1000);
  left.setSpeed(100);
  right.setSpeed(100);
  left.runSpeedToPosition();
  right.runSpeedToPosition();
  
}
void backwards(){
  
  left.moveTo(left.currentPosition() - 1000);
  right.moveTo(right.currentPosition() - 1000);
  left.setSpeed(100);
  right.setSpeed(100);
  left.runSpeedToPosition();
  right.runSpeedToPosition();
  
}
void turnRight(){
  
  left.moveTo(left.currentPosition() + 1000);
  right.moveTo(right.currentPosition() - 1000);
  left.setSpeed(100);
  right.setSpeed(100);
  left.runSpeedToPosition();
  right.runSpeedToPosition();
  
}
void turnLeft(){
  
  left.moveTo(left.currentPosition() - 1000);
  right.moveTo(right.currentPosition() + 1000);
  left.setSpeed(100);
  right.setSpeed(100);
  left.runSpeedToPosition();
  right.runSpeedToPosition();
  
}
