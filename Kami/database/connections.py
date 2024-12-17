from pymongo import MongoClient  # type: ignore
from pymongo.errors import ConnectionFailure  # type: ignore
from dotenv import load_dotenv  # type: ignore
import os

# Load environment variables
load_dotenv()

class MongoConnection:
    def __init__(self, uri: str):
        self.uri = uri
        self.client = None

    def connect(self):
        """Establish a connection to MongoDB."""
        try:
            self.client = MongoClient(self.uri)
            print("Connection to MongoDB Success")
            return self.client
        except ConnectionFailure:
            raise Exception("Connection to MongoDB failed")
        return None
    #When the bot disconnects
    def disconnect(self):
        """Close the connection to MongoDB."""
        if self.client:
            self.client.close()  # Close the MongoDB connection
            print("MongoDB connection closed.")
        else:
            print("No active connection to close.")
