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


boolean readyToMove = true;
int instruction = -2;     // Initializing to a number that instruction should never be set to again
//Motor pin setup
#define lStep  12 //Left step
#define lDir  10  //Left Direction
#define rStep  9 //Right Step
#define rDir  7 //Right Direction

#include <Stepper.h>
#include <AccelStepper.h>

#define STEPS 2038

Stepper drawMec(STEPS, 2,4,3,5);
AccelStepper left(AccelStepper::DRIVER , 9,7);
AccelStepper right(AccelStepper::DRIVER , 12,10);

void setup() {
  Serial.begin(9600);   // Should be the baud rate of the Pi
  Serial.setTimeout(6000);  // Setting a 1-min timeout for serial stuff just in case

  left.setSpeed(100);
  right.setSpeed(100);
  //lPos = left.currentPosition();
  //rPos = right.currentPosition();
  //left.setCurrentPosition (lPos);
  //right.setCurrentPosition (rPos);
  
/*
  //Pin assignment and setup for the left motor
  pinMode(lStep, OUTPUT);
  pinMode(lDir, OUTPUT);
  digitalWrite(lStep, LOW);
  digitalWrite(lDir, LOW);

  //Pin assignment for the right motor
  pinMode(rStep, OUTPUT);
  pinMode(rDir, OUTPUT);
  digitalWrite(rStep, LOW);
  digitalWrite(rDir, LOW);
*/


}

void loop() {
  // Constantly polls the serial port to check if there's a byte to read
  static int lPos = 0;
  static int rPos = 0;
  
  Serial.println("Waiting for instructions...");
  while(readyToMove) {
    // Since we're expecting bursts of instructions before requesting more, keep
    // pulling instructions (bytes) from the serial port until there aren't any left
    while(Serial.available() > 0) {
      readyToMove = false;
      instruction = Serial.read();
      Serial.println(instruction);
      
      // Once we've received a byte, print the appropriate instruction
      // Arduino uses ASCII values to represent ints
      switch(instruction) {
        case 48: 
        //Move Forwards
          lPos = lPos + 100;
          rPos = lPos +  100;
          break;
        case 49: 
        //Move Backwards
          lPos += -100;
          rPos += -100;
          break;
        case 50: 
        //Move Left
          lPos += 100;
          rPos += -100;
          break;
        case 51: 
        //Move Right
          lPos += -100;
          rPos += 100;
          break;
        case 52: 
        //Half Step Left Forwards
          //case4();  // ASCII 52 = int 4
          break;
        case 53: 
        //Hlaf Step Right Forwards
          //case5();    // ASCII 53 = int 5
          break;
        case 54: 
        //Half Step Left Backwards
          //case6();      // ASCII 54 = int 6
          break;
        case 55: 
        //Half Step Right Backwards
          //case7();      // ASCII 55 = int 7
          break;
        case 56: 
        //Half Step Left Backwards
          up();      // ASCII 54 = int 8
          break;
        case 57: 
        //Half Step Right Backwards
          down();      // ASCII 55 = int 9
          break;
        case 10: 
          Serial.println("Serial buffer empty"); // ASCII 10 is used as the end character 
          break;
        default: 
          Serial.print("Unexpected instruction number: ");
          Serial.println(instruction);
          break;
      }
      
    }
    delay(500);
  }
  Serial.println(lPos);
      left.moveTo(lPos);
      right.moveTo(rPos);
      left.runSpeedToPosition();
      right.runSpeedToPosition();
  // Updates readyToMove asks the Pi for more instructions
  // Sets instruction to an invalid number to avoid accidentally executing an instruction twice
  instruction = -1;
  readyToMove = true;
  Serial.write(6);  // ASCII 6 = ACK.  Shows up as a [] in the serial monitor.
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
