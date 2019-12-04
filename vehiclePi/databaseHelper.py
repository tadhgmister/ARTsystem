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

DATA = [(0, 0, 1.1255467237109016, 3.0213943841673463),
 (1, 0, 1.394243709787869, 3.0052081876347314),
 (2, 0, 1.6762205094901645, 2.9882849929861437),
 (3, 0, 1.970511091426102, 2.972720386393268),
 (4, 0, 2.2761494242039912, 2.960609954027787),
 (5, 0, 2.5921694764321432, 2.9540492820613853),
 (6, 0, 2.917605216718871, 2.955133956665748),
 (7, 0, 3.251490613672483, 2.965959564012558),
 (8, 0, 3.592859635901294, 2.9886216902735008),
 (9, 0, 3.940746252013613, 3.025215921620259),
 (10, 0, 4.294184430617753, 3.0778378442245162),
 (11, 0, 4.652208140322022, 3.1485830442579585),
 (12, 0, 5.013851349734734, 3.239547107892269),
 (13, 0, 5.378148027464202, 3.3528256212991314),
 (14, 0, 5.744132142118732, 3.490514170650229),
 (15, 0, 6.110837662306641, 3.654698321866856),
 (16, 0, 6.477298556636239, 3.846094794504741),
 (17, 0, 6.842548793715833, 4.062673236434122),
 (18, 0, 7.205622342153741, 4.302074951960392),
 (19, 0, 7.565553170558266, 4.561941245388937),
 (20, 0, 7.9213752475377275, 4.839913421025153),
 (21, 0, 8.272122541700433, 5.133632783174426),
 (22, 0, 8.616829021654693, 5.44074063614215),
 (23, 0, 8.954528656008822, 5.758878284233715),
 (24, 0, 9.284255413371127, 6.0856969623214),
 (25, 0, 9.605043262349923, 6.419281223236192),
 (26, 0, 9.91592617155352, 6.758307497112164),
 (27, 0, 10.215938109590232, 7.10149482630106),
 (28, 0, 10.504113045068364, 7.447562253154633),
 (29, 0, 10.77948494659623, 7.7952288200246365),
 (30, 0, 11.040871090842659, 8.143234459686145),
 (31, 0, 11.281500052665258, 8.490857889822244),
 (32, 0, 11.488653513334441, 8.837951144893783),
 (33, 0, 11.649324737149163, 9.184394064515063),
 (34, 0, 11.750506988408397, 9.53006648830039),
 (35, 0, 11.779193531411098, 9.874848255864052),
 (36, 0, 11.723090430654718, 10.218619206820357),
 (37, 0, 11.581876566470658, 10.561259180783598),
 (38, 0, 11.36516547195672, 10.90264801736808),
 (39, 0, 11.08302358121375, 11.242665556188102),
 (40, 0, 10.747631202627357, 11.581191636857959),
 (41, 0, 10.372716228322693, 11.918106098991952),
 (42, 0, 9.972042017184446, 12.253288782204383),
 (43, 0, 9.559371928097292, 12.586619526109548),
 (44, 0, 9.14846931994591, 12.91797817032175),
 (45, 0, 8.752121385281153, 13.246985883370536),
 (46, 0, 8.373525458590219, 13.57072264904887),
 (47, 0, 8.010435770882834, 13.88482610118114),
 (48, 0, 7.660544078523351, 14.184917318642324),
 (49, 0, 7.321542137876126, 14.466617380307389),
 (50, 0, 6.991121705305512, 14.725547365051309),
 (51, 0, 6.6669745371758635, 14.957994763041054),
 (52, 0, 6.34679238985154, 15.165024391067755),
 (53, 0, 6.028267019696896, 15.34978575453373),
 (54, 0, 5.709090183076282, 15.515025281596033),
 (55, 0, 5.386953636354056, 15.660948317562129),
 (56, 0, 5.059549135894574, 15.786791813075109),
 (57, 0, 4.724568438062187, 15.891790812489372),
 (58, 0, 4.379703299221254, 15.975180360159298),
 (59, 0, 4.022645475736131, 16.03619550043928),
 (60, 0, 3.6510867239711686, 16.074071277683707),
 (61, 0, 3.2627188002907226, 16.088042736246962),
 (62, 0, 2.855233461059152, 16.077344920483448),
 (63, 1, 20.022528515750746, 13.020357502726368),
 (64, 1, 19.718289130759423, 12.912148006550616),
 (65, 1, 19.37523894690903, 12.815713828907395),
 (66, 1, 19.00446462277288, 12.830056943995558),
 (67, 1, 18.617052816924275, 13.011880364941062),
 (68, 1, 18.224090187936536, 13.27597365499708),
 (69, 1, 17.83666339438296, 13.507434469143533),
 (70, 1, 17.465859094836855, 13.622418031939613),
 (71, 1, 17.122763947871537, 13.62473406489096),
 (72, 1, 16.818464612060307, 13.533545929071108),
 (73, 1, 16.56404774597648, 13.3680169855536),
 (74, 1, 16.370600008193357, 13.14731059541197),
 (75, 1, 16.24915266981334, 12.89055342387328),
 (76, 1, 16.202943811696144, 12.611708915892116),
 (77, 1, 16.219450317511026, 12.31429825461267),
 (78, 1, 16.28424772290248, 12.000582923574614),
 (79, 1, 16.382911563514988, 11.672824406317638),
 (80, 1, 16.501017374993022, 11.333284186381407),
 (81, 1, 16.62422152672673, 10.984223747305606),
 (82, 1, 16.742410313231648, 10.627904572629912),
 (83, 1, 16.851692730517183, 10.266588145894),
 (84, 1, 16.9486758751273, 9.90253595063755),
 (85, 1, 17.029966843605944, 9.538009470400235),
 (86, 1, 17.092172732497072, 9.175270188721736),
 (87, 1, 17.132020893676007, 8.816532050930851),
 (88, 1, 17.14942755916252, 8.46274840413542),
 (89, 1, 17.147752209331507, 8.113511442764542),
 (90, 1, 17.13052554748087, 7.768345675005659),
 (91, 1, 17.101278276908488, 7.426775609046212),
 (92, 1, 17.06354110091224, 7.088325753073634),
 (93, 1, 17.020844722790027, 6.752520615275369),
 (94, 1, 16.976719845839717, 6.418884703838852),
 (95, 1, 16.934697173359204, 6.086942526951524),
 (96, 1, 16.89830740864638, 5.756218592800824),
 (97, 1, 16.871081254999126, 5.426237409574189),
 (98, 1, 16.856549415715325, 5.096523485459058),
 (99, 1, 16.858242594092868, 4.766601328642872),
 (100, 1, 16.87969149342964, 4.435995447313066),
 (101, 1, 16.92442681702352, 4.104230349657079),
 (102, 1, 16.995979268172405, 3.7708305438623526),
 (103, 1, 17.097879550174174, 3.4353205381163243),
 (104, 1, 17.23365836632671, 3.0972248406064335),
 (105, 1, 17.40684641992791, 2.7560679595201174),
 (106, 1, 17.620974414275647, 2.4113744030448157),
 (107, 1, 17.879573052667816, 2.062668679367967),
 (108, 1, 18.186173038402302, 1.7094752966770097),
 (109, 1, 18.54430507477699, 1.3513187631593828),
 (110, 1, 18.957499865089762, 0.9877235870025246),
 (111, 1, 19.42928811263851, 0.618214276393874),
 (112, 1, 19.963200520721117, 0.24231533952087037),
 (113, 1, 20.562767792635462, -0.14044871542904858)]
if __name__ == "__main__":
    db = INIT_DATABASE()
    p = db.create_new_pattern(DATA, 24, 18)
    draw = db.create_drawing(p, Position(0,18), Position(24,0))
    print(draw)
    #
    # with db.cursor("SELECT id from drawings") as cursor:
    #     print(list(cursor))
    
    # with db.cursor("SELECT id from patterns") as cursor:
    #     print(list(cursor))
    # for thing in db.load_steps_for_pattern(1):
    #     print(thing)
        
