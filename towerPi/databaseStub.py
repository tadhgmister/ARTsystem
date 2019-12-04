# A class that accepts and stores any data, and provides a known tuple on a
# getStep request
class dataStub:
    
    def __init__(self):
        self.storage = []
        print("Initialized database.  Storage: " +str(self.storage))

    def log(self, *data, step):
        self.storage.append(data)
        print("Storage: " +str(self.storage))

    def getStep(self, drawingID, step):
        lines = (1, (1, (1, 1)))
        return lines
