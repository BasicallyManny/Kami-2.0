#Defines API endpoints that handle HTTP requests, validate input, and call MongoConnection methods.
from backend.models.coordinates import MinecraftCoordinate
from backend.schema.schemas import coordinates_serializer
from backend.config.connections import MongoConnection
from typing import Dict, Any, List
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException # type: ignore
from pymongo.collection import Collection # type: ignore


# Load environment variables
load_dotenv()
#intiaize mongoDB connection
mongoConnection=MongoConnection("mongoConnectionString")
mongoConnection.connect()
#create fastAPI router
router=APIRouter()
#GET REQUEST METHOD
DB_NAME = "minecraft_db"
COLLECTION_NAME = "coordinates"
@router.get("/")
async def get_coordinates():
    """Fetch all coordinates from MongoDB."""
    coordinates = list(mongoConnection.find_document(DB_NAME, COLLECTION_NAME, {}))
    return {"coordinates": coordinates_serializer(coordinates)}

@router.post("/coordinates")
async def add_coordinate(coordinate: MinecraftCoordinate):
    """Add a new coordinate to MongoDB."""
    inserted_id=mongoConnection.insert_document(DB_NAME, COLLECTION_NAME, coordinate.dict())
    return {"message:": "Coordinate added successfully", "id": inserted_id}

@router.delete("/{name}")
async def delete_coordinate(name: str):
    """Delete a coordinate from MongoDB."""
    deleted_count = mongoConnection.delete_document(DB_NAME, COLLECTION_NAME,  {"name": name})
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Coordinate not found")
    return {"message": f"Coordinate '{name}' deleted"}
