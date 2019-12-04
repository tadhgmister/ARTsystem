/* Code for serial communication between an Arduino and Pi
* Upon receiving a message, the Arduino will print "moving", wait for a few seconds,
* then send a singe byte serial message saying it's ready for the next message.
* 
* Version 1.1: added switch statement to avoid an avalanche of "if()"s
* Version 1.2: minor updates, initialized readyToMove to 'true' to avoid duplicate 
*   print statements
* 
* Author:  Scott Malonda 
* Version 1.2
* Date: Nov 16, 2019
*/

boolean readyToMove = true;
int instruction = -2;     // Initializing to a number that instruction should never be set to again

void setup() {
  Serial.begin(9600);   // Should be the baud rate of the Pi
  Serial.setTimeout(6000);  // Setting a 1-min timeout for serial stuff just in case
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
          Serial.println("Forward");  // ASCII 48 = int 0
          break;
        case 49:
          Serial.println("Backward");
          break;
        case 50: 
          Serial.println("Right");     // ASCII 50 = int 2
          break;
        case 51: 
          Serial.println("Left");      // ASCII 51 = int 3
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
    delay(500); // Without this delay the program keeps exiting the while loop for some reason
  }

  // Updates readyToMove asks the Pi for more instructions
  // Sets instruction to an invalid number to avoid accidentally executing an instruction twice
  instruction = -1;
  readyToMove = true;
  Serial.write(6);  // ASCII 6 = ACK.  Shows up as a [] in the serial monitor.
}
