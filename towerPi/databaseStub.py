# A class that just accepts and stores any data
class dataStub:
    
    def __init__(self):
        self.storage = []
        print("Initialized database.  Storage: " +str(self.storage))

    def log(self, *data):
        self.storage.append([data])
        print("Storage: " +str(self.storage))
