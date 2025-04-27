from fastapi import APIRouter, HTTPException
from models.coordinates import MinecraftCoordinate, CoordinateUpdatePayload
from config.connections import MongoConnection
from typing import List
from dotenv import load_dotenv
import os
from pydantic import ValidationError
from bson import ObjectId

# Create fastAPI router
coordinateRouter = APIRouter()

# Load environment variables
load_dotenv()

# Create mongo instance
mongoConnectionString = os.getenv("mongoConnectionString")
MongoConnection = MongoConnection(mongoConnectionString)

DB_NAME = "test_db"
COLLECTION_NAME = "test_coordinates"

# Helper function to convert MongoDB documents to Pydantic model
def mongo_to_pydantic(coord):
    if '_id' in coord:
        coord['_id'] = str(coord['_id'])  # Convert ObjectId to string
    return MinecraftCoordinate(**coord)

# ROUTE METHODS

@coordinateRouter.get("/coordinates", response_model=List[MinecraftCoordinate])
async def get_all_coordinates():
    """ Retrieves all Minecraft coordinates stored in the database. """
    try:
        coordinates = MongoConnection.find_documents(DB_NAME, COLLECTION_NAME, {})
        
        if not coordinates:
            raise HTTPException(status_code=404, detail="No coordinates found in the database.")
        
        return [mongo_to_pydantic(coord) for coord in coordinates]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@coordinateRouter.get("/coordinates/{guild_id}", response_model=List[MinecraftCoordinate])
async def get_coordinates_by_guild(guild_id: str):
    """ Retrieves all Minecraft coordinates stored in the database for a specific guild. """
    try:
        coordinates = MongoConnection.find_documents(DB_NAME, COLLECTION_NAME, {"guild_id": guild_id})

        if not coordinates:
            return []  # Return an empty list

        return [mongo_to_pydantic(coord) for coord in coordinates]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@coordinateRouter.get("/coordinates/{guild_id}/{coordinate_name}", response_model=List[MinecraftCoordinate])
async def get_coordinate(guild_id: str, coordinate_name: str):
    """ Retrieves a Minecraft coordinate from the database by its name. """
    try:
        coordinates = MongoConnection.find_documents(
            DB_NAME,
            COLLECTION_NAME,
            {"guild_id": guild_id, "coordinateName": coordinate_name}
        )

        if not coordinates:
            raise HTTPException(status_code=404, detail="Coordinate Name not found")

        return [mongo_to_pydantic(coord) for coord in coordinates]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@coordinateRouter.post("/coordinates/{guild_id}/{coordinate_name}", response_model=MinecraftCoordinate)
async def add_coordinate(guild_id: str, coordinate_name: str, coordinate: MinecraftCoordinate):
    """ Adds a new Minecraft coordinate to the database. """
    try:
        coordinate.guild_id = guild_id
        coordinate.coordinateName = coordinate_name
        payload = coordinate.dict(by_alias=True, exclude_none=True)
         # Remove the duplicate id field if both exist
        if "id" in payload and "_id" in payload:
            del payload["id"]
        MongoConnection.insert_document(DB_NAME, COLLECTION_NAME, payload)
        return coordinate
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@coordinateRouter.put("/coordinates/{coordinate_id}", response_model=CoordinateUpdatePayload)
async def overwrite_coordinate(guild_id: str, coordinate_id: str, coordinate: CoordinateUpdatePayload):
    """ Updates an existing Minecraft coordinate in the database by object ID. """
    try:
        coordinate_id = ObjectId(coordinate_id)
        
        # Convert payload to dict and remove None values to avoid overwriting fields
        update_data = {k: v for k, v in coordinate.dict().items() if v is not None}
        
        updated_count = MongoConnection.update_document(
            DB_NAME, COLLECTION_NAME, {"_id": coordinate_id, "guild_id": guild_id}, update_data
        )

        if updated_count == 0:
            raise HTTPException(status_code=404, detail="Coordinate not found")

        # Fetch the updated document to return
        updated_coordinate = MongoConnection.get_document(
            DB_NAME, COLLECTION_NAME, {"_id": coordinate_id}
        )
        
        if not updated_coordinate:
            raise HTTPException(status_code=404, detail="Failed to retrieve updated coordinate")
            
        return CoordinateUpdatePayload(**updated_coordinate)
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@coordinateRouter.delete("/coordinates/{guild_id}/{coordinate_name}")
async def delete_coordinate(guild_id: str, coordinate_name: str):
    """ Deletes a Minecraft coordinate by its name. """
    try:
        deleted_count = MongoConnection.delete_document(
            DB_NAME, COLLECTION_NAME, {"guild_id": guild_id, "coordinateName": coordinate_name}
        )

        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="Coordinate not found")

        return {"message": "Coordinate deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@coordinateRouter.delete("/coordinates/{guild_id}")
async def clear_coordinates(guild_id: str):
    """ Deletes all Minecraft coordinates from the database for a specific guild. """
    try:
        result = MongoConnection.clear_documents(DB_NAME, COLLECTION_NAME, {"guild_id": guild_id})

        if result.deleted_count == 0:
            return {"message": "No coordinates found for this guild, nothing to delete"}

        return {"message": f"Deleted {result.deleted_count} coordinates successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
