from pymongo import MongoClient

class MongoConnection:
    def __init__(self, uri: str):
        self.uri = uri
        self.client = None

    def connect(self):
        self.client = MongoClient(self.uri)
        print("Connected to MongoDB")

    def disconnect(self):
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")
