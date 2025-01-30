from pymongo import MongoClient  # type: ignore


class MongoConnection:
    """Manages MongoDB connections and operations."""
    def __init__(self, uri: str):
        self.uri = uri
        self.client = None

    def connect(self):
        """Connect to MongoDB"""
        self.client = MongoClient(self.uri)
        print("Connected to MongoDB")

    def disconnect(self):
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

    def get_db(self, db_name: str):
        """Gets or creates the database with the given name."""
        if self.client:
            return self.client[db_name]
        else:
            raise Exception("Not connected to MongoDB")

    def insert_document(self, db_name: str, collection_name: str, document: dict):
        """Insert a document into a collection"""
        db = self.get_db(db_name)
        collection = db[collection_name]
        result = collection.insert_one(document)
        return str(result.inserted_id)

    def delete_document(self, db_name: str, collection_name: str, query: dict):
        """Delete a document from a collection"""
        db = self.get_db(db_name)
        collection = db[collection_name]
        result = collection.delete_one(query)
        return result.deleted_count

    def update_document(self, db_name: str, collection_name: str, query: dict, update: dict):
        """Update a document in a collection"""
        db = self.get_db(db_name)
        collection = db[collection_name]
        result = collection.update_one(query, {"$set": update})
        return result.modified_count

    def find_document(self, db_name: str, collection_name: str, query: dict):
        """Find documents from a collection"""
        db = self.get_db(db_name)
        collection = db[collection_name]
        return collection.find(query)
