import sqlite3
import contextlib
import datetime
import collections
import typing
try:
    from common import Position
except ImportError:
    from .common import Position

class _Ref:
    """foreign key ref to another table"""
    def __init__(self,table,field):
        self.table = table
        self.field = field
    
_ID = (int)#,  "AUTOINCREMENT")
# contains the text expected in sql definitions for corresponding python types
TYPE_CONVS = {bool:"bit", str:"text", int:"integer", float:"numeric",
              datetime.datetime:"timestamp"}
# Field definitions for all the tables
# each key of this corresponds to a table, each key of the table corresponds to a field
# except for the key "PRIMARY KEY" which just denotes what the primary key is.
# for the value of each field will be the python type or a tuple which the first value is a python type
# and remaining elements are strings to be passed to the declaration in sql, like "AUTO_INCREMENT"
TABLE_DATA = {
    "patterns":{
        "id": _ID,
        "error": str,
        "numOfSteps": int,
        "width": int,
        "height":int,
        "PRIMARY KEY": "(id)"
    },
    "patternSteps":{
        "patternId":_Ref("patterns","id"),
        "stepIndex":int,
        "lineIndex": int,
        "x":float,
        "y":float,
        "PRIMARY KEY": "(patternId, stepIndex)"
    },
    "drawings":{
        "id": _ID,
        "patternUsed": _Ref("patterns","id"),
        "bound1x":float,
        "bound1y":float,
        "bound2x":float,
        "bound2y":float,
        "timeInitialized":datetime.datetime,
        "currentStep":_Ref("patternSteps","stepIndex"),
        "updateNotification": str,
        "PRIMARY KEY": "(id)"
    },
    "logs": {
        "id": _ID,
        "patternStep": _Ref("patternSteps", "stepIndex"),
        "drawingID":_Ref("drawings","id"),
        "timestamp":datetime.datetime,
        "x":float,
        "y":float,
        "facing":float,
        "requested":bool,
        "PRIMARY KEY": "(id)"
    }
}

def _parse_typedef(data):
    if isinstance(data,tuple):
        [type, *rest] = data
        return " ".join([_parse_typedef(type), *rest])
    elif data in TYPE_CONVS.keys():
        return TYPE_CONVS[data]
    elif isinstance(data, _Ref):
        return _parse_typedef(TABLE_DATA[data.table][data.field])
    elif isinstance(data, str):
        return data
    else:
        raise TypeError(f"Unrecognized definition: {data!r}")
    
def _makeCreateTableEntries(table: str):
    foreignKeys = []
    for field, data in TABLE_DATA[table].items():
        if isinstance(data, _Ref):
            foreignKeys.append((field,data))
        data_str = _parse_typedef(data)
        yield f"{field} {data_str}"
    for fieldname, ref in foreignKeys:
        yield f"FOREIGN KEY ({fieldname}) REFERENCES {ref.table} ({ref.field})"
        
def _makeCreateTableCommand(table:str):
    field_defs = ",\n    ".join(_makeCreateTableEntries(table))
    return f"""
CREATE TABLE IF NOT EXISTS {table} (
    {field_defs}
);"""

CREATE_TABLE_SCRIPT = "\n\n".join(map(_makeCreateTableCommand, TABLE_DATA.keys()))

def fields_of_table(table:str):
    def _not_primekey(field):
        return field != "PRIMARY KEY"
    return filter(_not_primekey, TABLE_DATA[table])

PatternsEntry = collections.namedtuple("PatternsEntry", fields_of_table("patterns"))
StepEntry = collections.namedtuple("StepEntry", fields_of_table("patternSteps"))
DrawingEntry = collections.namedtuple("DrawingEntry", fields_of_table("drawings"))
LogEntry = collections.namedtuple("LogEntry", fields_of_table("logs"))


class Database:
    
    def __init__(self, file="testDB.db"):
        self.conn = sqlite3.connect(file, detect_types=sqlite3.PARSE_DECLTYPES)
    @contextlib.contextmanager
    def cursor(self, *command, commit:bool=None):
        """creates a cursor for a context manager,
        if given, command is sql command to run before returning it.
        if no command is given it is assumed mutative operations, so after the with statement
        the changes are commited to the database.
        When a command is given it will not commit unless commit=True is given.
        """
        cursor = self.conn.cursor()
        if command:
            cursor.execute(*command)
        try:
            yield cursor
        finally:
            cursor.close()
        # this is only called when no error is raised, if an error happens
        # in the with statement it is thrown by the yield.
        if commit is True or (commit is None and not command):
            self.conn.commit()
        
        
    
    def create_tables(self):
        """runs the create tables script"""
        with self.cursor() as cursor:
            cursor.executescript(CREATE_TABLE_SCRIPT)

##################### INSERT FUNCTIONS ##################### 
            
    def create_new_pattern(self, points_iter, width, height):
        """
        creates a new pattern in the database including all the relevent
        pattern steps and returns the pattern ID.
        points_iter is a sorted iterator that generates tuples:
            (stepIndex,lineIndex,x,y)
        in the same format put in the database, the x,y are in pixels.
        width and height are the width and height of the canvas.
        """
        with self.cursor() as cursor:
            # create a new entry in pattern table, id will be autogenerated
            # only the width and height need to be specified
            cursor.execute("""INSERT INTO patterns(width, height)
                           VALUES (?,?)""", (width, height))
            #read the pattern ID generated.
            patternId = cursor.lastrowid
            #for convinience we will put the patternId directly into the string so we can pass
            #points_iter directly, this is not generally recommended but we are reading it from
            # the database row so we aren't really at risk of it causing sql insert stuff.
            cursor.executemany(f"""INSERT INTO patternSteps (patternId, stepIndex,lineIndex, x, y)
                                 VALUES ({patternId}, ?,?,?,?)""", points_iter)
        return patternId
            
    def create_drawing(self, patternId, bound1: Position, bound2: Position):
        """creates a new fully calibrated drawing entry and returns the drawingId"""
        initTime = datetime.datetime.now()
        with self.cursor() as cursor:
            #TODO: do error checking on bounds? make sure that bound1 has lower x,y than bound2
            # more specifically, correct it in the event it isn't that way.
            cursor.execute("""INSERT INTO drawings
            (patternUsed, bound1x,bound1y,bound2x,bound2y,timeInitialized,currentStep,updateNotification)
                VALUES (?,?,?,?,?,?,?,?)""",
                (patternId, bound1.x, bound1.y, bound2.x, bound2.y, initTime, 0, "")
            )
            return cursor.lastrowid

    def add_log_entry(self, drawingId, pos: Position, step=None, requested=False, timestamp="NOW"):
        """adds a log entry for given drawing. """
        if timestamp == "NOW":
            timestamp = datetime.datetime.now()
        elif not isinstance(timestamp, datetime.datetime):
            raise TypeError("timestamp must be omitted or a datetime object")

        with self.cursor() as cursor:
            cursor.execute("""INSERT INTO logs
                (patternStep,drawingId,timestamp,x,y,orientation,requested)
                VALUES (?,?,?,?,?,?,?)""",
                (step, drawingId, timestamp, pos.x, pos.y, pos.facing, requested)
            )
            return cursor.lastrowid

##################### GET FUNCTIONS #####################                  

    
    
    def load_pattern_info(self, patternId) -> PatternsEntry:
        """returns data on pattern, throws ValueError if pattern does not exist."""
        fields = ", ".join(PatternsEntry._fields)
        with self.cursor(f"SELECT {fields} FROM patterns WHERE id=?",(patternId,)) as cursor:
            result = cursor.fetchall()
            if len(result) == 0:
                raise ValueError(f"pattern not found: {patternId}")
            assert len(result) <= 1, "multiple patterns found?"
            return PatternsEntry(*result[0])

    def load_drawing_info(self, drawingId) -> DrawingEntry:
        """returns data on drawing, throws ValueError if drawing does not exist."""
        fields = ", ".join(DrawingEntry._fields)
        with self.cursor(f"SELECT {fields} FROM drawings WHERE id=?",(drawingId,)) as cursor:
            result = cursor.fetchall()
            if len(result) == 0:
                raise ValueError(f"drawing not found: {drawingId}")
            assert len(result) <= 1, "multiple drawings found?"
            return DrawingEntry(*result[0])

    def load_logs_for_drawing(self, drawingId) -> typing.Generator[LogEntry,None,None]:
        """generates a series of LogEntry objects for all log entries for the given drawing
        *if the drawing does not exist no check is made* and empty iterator is returned."""
        fields = ", ".join(LogEntry._fields)
        with self.cursor(f"SELECT {fields} FROM logs WHERE drawingId=?",(drawingId,)) as cursor:
            # use yield from so that after all are done with statement will still close the cursor.
            yield from map(LogEntry._make, cursor)

    def load_steps_for_pattern(self, patternId) -> typing.Generator[StepEntry,None,None]:
        """generates a series of StepEntry objects for all steps in given pattern
        if there are no steps for the given pattern an error is thrown."""
        fields = ", ".join(StepEntry._fields)
        with self.cursor(f"SELECT {fields} FROM patternSteps WHERE patternId=?",(patternId,)) as cursor:
            # will check that we have at least one entry, otherwise we should throw an error instead of just yielding no items.
            first_one = cursor.fetchone()
            if first_one is None:
                raise ValueError(f"can't find any steps for pattern {patternId}")
            yield StepEntry(*first_one)
            # use yield from so that after all are done with statement will still close the cursor.
            yield from map(StepEntry._make, cursor)


def INIT_DATABASE(file="testDB.db"):
    import os
    os.remove(file)
    db = Database(file)
    db.create_tables()
    from towerCommunication import load_points_for_drawing_MOCK
    all_points = list(load_points_for_drawing_MOCK(1))
    [step,line,x,y] = zip(*all_points)
    pID = db.create_new_pattern(all_points, max(x), max(y))
    loBound = Position(10,60)
    hiBound = Position(60,10)
    dID = db.create_drawing(pID, loBound, hiBound)

    print("new pattern",pID, "and new drawing",dID)
    return db

db = Database()
if __name__ == "__main__":
    db = INIT_DATABASE()
    with db.cursor("SELECT id from drawings") as cursor:
        print(list(cursor))
    
    with db.cursor("SELECT id from patterns") as cursor:
        print(list(cursor))
    for thing in db.load_steps_for_pattern(1):
        print(thing)
        
