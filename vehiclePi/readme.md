# Vehicle Pi

This folder contains all the code intended to be run on the vehicle pi

The entire folder can be run from command line by running this from the folder above:
`python3 -m vehiclePi -h`
this will output help message, this program will run the drawing program for the drawing ID given by command line argument.

Each module is written so that running it as the main python file will run tests for that module to make testing easier. the files with "test" in the name were written as proof of concepts and aren't necessarily inteded to be used in the final product.  "sqltest" was replaced with "databaseHelper" and "serialtest" was replaced by "serialCommunication"