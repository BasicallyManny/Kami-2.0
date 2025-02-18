from fastapi import APIRouter, HTTPException
from models.coordinates import MinecraftCoordinate, CoordinateUpdatePayload
from config.connections import MongoConnection
from typing import List
from dotenv import load_dotenv
import os
from pydantic import ValidationError

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
        MongoConnection.insert_document(DB_NAME, COLLECTION_NAME, coordinate.dict())
        return coordinate
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@coordinateRouter.put("/coordinates/{guild_id}/{coordinate_name}", response_model=MinecraftCoordinate)
async def overwrite_coordinate(guild_id: str, coordinate_name: str, coordinate: MinecraftCoordinate):
    """ Updates an existing Minecraft coordinate in the database. """
    try:
        existing = MongoConnection.find_one_document(
            DB_NAME, COLLECTION_NAME,
            {"coordinateName": coordinate_name, "guild_id": guild_id}
        )

        if not existing:
            raise HTTPException(status_code=404, detail="Coordinate not found")

        MongoConnection.update_document_element(DB_NAME, COLLECTION_NAME, {"coordinateName": coordinate_name, "guild_id": guild_id}, coordinate.dict())
        return coordinate
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@coordinateRouter.patch("/coordinates/{guild_id}/{coordinate_name}", response_model=MinecraftCoordinate)
async def update_coordinate(
    guild_id: str,
    coordinate_name: str,
    update_data: CoordinateUpdatePayload
):
    """ Update a coordinate's name and/or coordinates in the database. """
    try:
        new_name = update_data.new_name
        coordinates = update_data.coordinates

        if not new_name and not coordinates:
            raise HTTPException(status_code=400, detail="Either new_name or coordinates must be provided")

        existing = MongoConnection.find_one_document(
            DB_NAME, COLLECTION_NAME,
            {"coordinateName": coordinate_name, "guild_id": guild_id}
        )

        if not existing:
            raise HTTPException(status_code=404, detail="Coordinate not found")

        if new_name:
            name_exists = MongoConnection.find_one_document(
                DB_NAME, COLLECTION_NAME,
                {"coordinateName": new_name, "guild_id": guild_id, "_id": {"$ne": existing["_id"]}}
            )

            if name_exists:
                raise HTTPException(status_code=400, detail=f"Coordinate name '{new_name}' already exists.")

        update_fields = {}
        if coordinates:
            update_fields["coordinates"] = coordinates.dict()
        if new_name:
            update_fields["coordinateName"] = new_name

        updated_doc = MongoConnection.update_and_return_document(
            DB_NAME,
            COLLECTION_NAME,
            {"coordinateName": coordinate_name, "guild_id": guild_id},
            update_fields
        )

        if not updated_doc:
            raise HTTPException(status_code=400, detail="Update failed. No changes made.")

        return mongo_to_pydantic(updated_doc)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

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
