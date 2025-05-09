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
            self.client = MongoClient(self.uri)
            self.client.admin.command("ping")  # Test connection
        except PyMongoError as e:
            raise Exception("Failed to connect to MongoDB.")    

    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
        else:
            raise Exception("Not connected to MongoDB")

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
    
    def get_document(self, db_name: str, collection_name: str, query: dict):
        """Retrieve a single document from a collection"""
        db = self.get_db(db_name)
        collection = db[collection_name]
        return collection.find_one(query)

    def insert_document(self, db_name: str, collection_name: str, document: dict):
        """Insert a document into a collection"""
        db = self.get_db(db_name)
        collection = db[collection_name]
        result = collection.insert_one(document)
        return str(result.inserted_id)

    def find_documents(self, db_name: str, collection_name: str, query: dict):
        """Retrieve documents from a collection with proper ObjectId handling."""
        collection = self.get_db(db_name)[collection_name]
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
    # Update the MongoDB helper method to return the updated document
    def update_and_return_document(self, db_name: str, collection_name: str, query: dict, update_fields: dict):
        """
        Update multiple fields in a document and return the updated document.

        """
        db = self.get_db(db_name)
        collection = db[collection_name]
    
        result = collection.find_one_and_update(
            query,
            {"$set": update_fields},
            return_document=True  # Return the document after the update
        )
    
        if not result:
            return Exception("Document not found or update failed")
        
        return result
    
    def find_one_document(self, db_name: str, collection_name: str, query: dict):
        """Find a single document in a collection based on the query"""
        db = self.get_db(db_name)
        collection = db[collection_name]
        return collection.find_one(query)
