/* Code for serial communication between an Arduino and Pi
* Upon receiving a message, the Arduino will activate the motor controls for the instruction,
* wait for a few seconds,
* then send a singe byte serial message saying it's ready for the next message.
* 
* Version 1.1: added switch statement to avoid an avalanche of "if()"s
* Version 1.2: minor updates, initialized readyToMove to 'true' to avoid duplicate 
*   print statements
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
#define rStep  8 //Right Step
#define rDir  6 //Right Direction
#define ChalkB  4 //Chalk Mech 1
#define ChalkR  3 //Chalk Mech 2

void setup() {
  Serial.begin(9600);   // Should be the baud rate of the Pi
  Serial.setTimeout(6000);  // Setting a 1-min timeout for serial stuff just in case
  
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

  //Pin assignment for the chalk mechanism
  pinMode(ChalkB, OUTPUT);
  pinMode(ChalkR, INPUT);
  digitalWrite(ChalkB, LOW);
  digitalWrite(ChalkR, LOW);
}

void loop() {
  // Constantly polls the serial port to check if there's a byte to read
  Serial.println("Waiting for instructions...");
  while(readyToMove) {
    // Since we're expecting bursts of instructions before requesting more, keep
    // pulling instructions (bytes) from the serial port until there aren't any left
    while(Serial.available() > 0) {
      readyToMove = false;
      instruction = Serial.read();
      
      // Once we've received a byte, print the appropriate instruction
      // Arduino uses ASCII values to represent ints
      switch(instruction) {
        case 48: 
        //Move Forwards
          case0();  // ASCII 48 = int 0
          break;
        case 49: 
        //Move Backwards
          case1();    // ASCII 49 = int 1
          break;
        case 50: 
        //Move Left
          case2();      // ASCII 50 = int 2
          break;
        case 51: 
        //Move Right
          case3();      // ASCII 51 = int 3
          break;
        case 52: 
        //Half Step Left Forwards
          case4();  // ASCII 52 = int 4
          break;
        case 53: 
        //Hlaf Step Right Forwards
          case5();    // ASCII 53 = int 5
          break;
        case 54: 
        //Half Step Left Backwards
          case6();      // ASCII 54 = int 6
          break;
        case 55: 
        //Half Step Right Backwards
          case7();      // ASCII 55 = int 7
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

  // Updates readyToMove asks the Pi for more instructions
  // Sets instruction to an invalid number to avoid accidentally executing an instruction twice
  instruction = -1;
  readyToMove = true;
  Serial.write(6);  // ASCII 6 = ACK.  Shows up as a [] in the serial monitor.
}
//Cases for motor movement
void case0(){//Forwards
  digitalWrite(lDir, LOW);
  digitalWrite(rDir, HIGH);
  digitalWrite(lStep, HIGH);
  digitalWrite(rStep, HIGH);
  delayMicroseconds(2000);
  digitalWrite(lStep, LOW);
  digitalWrite(rStep, LOW);
  delayMicroseconds(2000);
}
void case1(){//Backwards
  digitalWrite(lDir, HIGH);
  digitalWrite(rDir, LOW);
  digitalWrite(lStep, HIGH);
  digitalWrite(rStep, HIGH);
  delayMicroseconds(2000);
  digitalWrite(lStep, LOW);
  digitalWrite(rStep, LOW);
  delayMicroseconds(2000);
}
void case2(){ //Left
  digitalWrite(lDir, HIGH);
  digitalWrite(rDir, HIGH);
  digitalWrite(lStep, HIGH);
  digitalWrite(rStep, HIGH);
  delayMicroseconds(2000);
  digitalWrite(lStep, LOW);
  digitalWrite(rStep, LOW);
  delayMicroseconds(2000);
}
void case3(){//Right
  digitalWrite(lDir, LOW);
  digitalWrite(rDir, LOW);
  digitalWrite(lStep, HIGH);
  digitalWrite(rStep, HIGH);
  delayMicroseconds(2000);
  digitalWrite(lStep, LOW);
  digitalWrite(rStep, LOW);
  delayMicroseconds(2000);
}
void case4(){//Half Step Left
  digitalWrite(rDir, HIGH);
  digitalWrite(rStep, HIGH);
  delayMicroseconds(2000);
  digitalWrite(rStep, LOW);
  delayMicroseconds(2000);
}
void case5(){//Half Step Right
  digitalWrite(rDir, LOW);
  digitalWrite(rStep, HIGH);
  delayMicroseconds(2000);
  digitalWrite(rStep, LOW);
  delayMicroseconds(2000);
}
void case6(){// Half Step Left Back
  digitalWrite(lDir, HIGH);
  digitalWrite(lStep, HIGH);
  delayMicroseconds(2000);
  digitalWrite(lStep, LOW);
  delayMicroseconds(2000);
}
void case7(){// Half Step Right Back
  digitalWrite(lDir, LOW);
  digitalWrite(lStep, HIGH);
  delayMicroseconds(2000);
  digitalWrite(lStep, LOW);
  delayMicroseconds(2000);
}

void clear(){//Clears all motor commands

digitalWrite(lStep, LOW);
digitalWrite(lDir, LOW);
digitalWrite(rStep, LOW);
digitalWrite(rDir, LOW);

}
