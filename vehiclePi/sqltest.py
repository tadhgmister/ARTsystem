##import mysql.connector
import sqlite3
from pprint import pprint
import towerCommunication

CREATE_TABLE_COMMANDS = ["""
CREATE TABLE IF NOT EXISTS patterns (
    id integer AUTO_INCREMENT,
    --image ????,
    error text,
    numOfSteps integer,
    width integer,
    height integer,
    PRIMARY KEY (id)
); """, """
CREATE TABLE IF NOT EXISTS patternSteps (
    patternId integer NOT NULL,
    stepIndex integer NOT NULL,
    lineIndex integer,
    x numeric,
    y numeric,
    PRIMARY KEY (patternID, stepIndex),
    FOREIGN KEY (patternID) REFERENCES patterns (id)
); """, """
CREATE TABLE IF NOT EXISTS drawings (
    id integer AUTO_INCREMENT,
    patternUsed integer NOT NULL,
    bound1x numeric,
    bound1y numeric,
    bound2x numeric,
    bound2y numeric,
    timeInitialized text,
    currentStep integer,
    updateNotification text,

    FOREIGN KEY (patternUsed) REFERENCES patterns (id),
    FOREIGN KEY (currentStep) REFERENCES patternSteps (stepIndex),
    PRIMARY KEY (id)
    
);""", """
CREATE TABLE IF NOT EXISTS logs (
    entryId integer AUTO_INCREMENT,
    patternStep integer,
    drawingID integer,timestamp text,
    x numeric,
    y numeric,
    orientation numeric,
    requested bit,
    --snapshot: ???,
    
    FOREIGN KEY (patternStep) REFERENCES patternSteps (stepIndex),
    FOREIGN KEY (drawingID) REFERENCES drawings (id)
    PRIMARY KEY (entryId)
); """]
def create_tables(mydb):
    cursor = mydb.cursor()
    
    for command in CREATE_TABLE_COMMANDS:
        cursor.execute(command)
    mydb.commit()
def create_new_pattern(mydb, lines_iterator, width, height):
    cursor = mydb.cursor()
    command = f"""
INSERT INTO patterns(width, height)
            VALUES ({width},{height});"""
    cursor.execute(command)
    patternId = cursor.lastrowid
    
    for line_id, line_iter in lines_iterator:
        for (stepID, (x,y)) in line_iter:
            command = f"""
INSERT INTO patternSteps (patternId, stepIndex,lineIndex, x, y)
                VALUES ({patternId}, {stepID}, {line_id}, {x}, {y});"""
            cursor.execute(command)
    mydb.commit()
    return patternId
##
##mydb = mysql.connector.connect(host="localhost",
##                              user="root", password="Wonder6!",
##                              auth_plugin='mysql_native_password')

towerCommunication.load_points_for_drawing = towerCommunication.load_points_for_drawing_MOCK
mydb = sqlite3.connect("./testDB.db")
try:
    #create_tables(mydb)
    points = towerCommunication.get_lines_of_drawing(1)
    patternid = create_new_pattern(mydb, points, 50, 50)
##    patternid = 1
    print(patternid)
##    cursor = 
##    cursor.execute("SELECT stepIndex, lineIndex, x, y FROM patternSteps WHERE patternId=?", (patternid,))
##    for stuff in cursor:
##        print(stuff)
finally:
    mydb.close()
