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
