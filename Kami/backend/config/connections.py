from pymongo import MongoClient
from pymongo.errors import PyMongoError
from urllib.parse import urlparse


class MongoConnection:
    """Handles MongoDB connection and basic database operations"""

    def __init__(self, uri: str):
        self.uri = uri
        self.client = None
        self.connect()

    def connect(self):
        """Establish a connection to MongoDB"""
        try:
            parsed_uri = urlparse(self.uri)
            cluster_name = parsed_uri.hostname  # Extract cluster name
            print(f"MongoDB URI (connections): {parsed_uri}")
            print(f"Attempting to connect to MongoDB cluster: {cluster_name}")

            self.client = MongoClient(self.uri)
            self.client.admin.command("ping")  # Test connection
            print("Connected to MongoDB through Connections")
        except PyMongoError as e:
            print(f"Error connecting to MongoDB: {e}")
            raise Exception("Failed to connect to MongoDB.")    

    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")
        else:
            print("No active MongoDB connection to disconnect.")

    def get_db(self, db_name: str):
        """Retrieve the specified database"""
        if not self.client:
            raise Exception("Not connected to MongoDB")

        # Check if the database exists
        db_list = self.client.list_database_names()
        if db_name not in db_list:
            raise Exception(f"Database '{db_name}' does not exist")

        return self.client[db_name]

        
    def get_collection(self, db_name: str, collection_name: str):
        """Retrieve the specified collection"""
        db = self.get_db(db_name)
        return db[collection_name]

    def insert_document(self, db_name: str, collection_name: str, document: dict):
        """Insert a document into a collection"""
        db = self.get_db(db_name)
        collection = db[collection_name]
        result = collection.insert_one(document)
        return str(result.inserted_id)

    def find_documents(self, db_name: str, collection_name: str, query: dict):
        """Retrieve documents from a collection"""
        db = self.get_db(db_name)
        collection = db[collection_name]
        return list(collection.find(query)) 


    def delete_document(self, db_name: str, collection_name: str, query: dict):
        """Delete a document from a collection"""
        db = self.get_db(db_name)
        collection = db[collection_name]
        result = collection.delete_one(query)
        return result.deleted_count
    
    def clear_documents(self, db_name: str, collection_name: str, filter_query: dict):
        """Clear documents matching the filter from a collection"""
        db = self.get_db(db_name)
        collection = db[collection_name]
        return collection.delete_many(filter_query)
    
    def update_document(self, db_name: str, collection_name: str, query: dict, update: dict):
        """Update a document in a collection"""
        db = self.get_db(db_name)
        collection = db[collection_name]
        result = collection.update_many(query, {"$set": update})
        return result.modified_count

    def update_document_element(self, db_name: str, collection_name: str, query: dict, update: dict):
        """Update a document in a collection"""
        db = self.get_db(db_name)
        collection = db[collection_name]
        result = collection.update_one(query, {"$set": update})
        return result.modified_count
    
    def find_one_document(self, db_name: str, collection_name: str, query: dict):
        """Find a single document in a collection based on the query"""
        db = self.get_db(db_name)
        collection = db[collection_name]
        return collection.find_one(query)
