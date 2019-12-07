# arduino logic

This folder contains arduino code.  the arduino is responsible for taking commands via serial from vehiclePi and in turn controlling the motors on the vehicle.

We ran into several issues with this where the code to control the wheels couldn't do both sides at the same time, so we used a library, but working code from the library stopped working when serial communication was done at the same time so these files aren't totatlly finished.