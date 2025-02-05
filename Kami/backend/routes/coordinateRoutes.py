# Defines API endpoints that handle HTTP requests, validate input, and call MongoConnection methods.
from models.coordinates import MinecraftCoordinate
from config.connections import MongoConnection
from typing import List, Optional

from fastapi import APIRouter, HTTPException # type: ignore
from dotenv import load_dotenv
import os

# Create fastAPI router
coordinateRouter = APIRouter()
#load enviropment variables
load_dotenv()
#create mongo instance
mongoConnectionString = os.getenv("mongoConnectionString")
MongoConnection = MongoConnection(mongoConnectionString)

DB_NAME = "test_db"
COLLECTION_NAME = "test_coordinates"

# ROUTE METHODS
@coordinateRouter.get("/coordinates", response_model=List[MinecraftCoordinate])
async def get_all_coordinates():
    """
    Retrieves all Minecraft coordinates stored in the database.
    """
    try:
        coordinates = MongoConnection.find_documents(DB_NAME, COLLECTION_NAME, {})

        if not coordinates:
           raise HTTPException(status_code=404, detail="No coordinates found in the database.")

        # Ensure _id is properly converted to string and coordinates is a list of dictionaries
        for coord in coordinates:
            if '_id' in coord:  # MongoDB _id field handling
                coord['_id'] = str(coord['_id'])  # Convert ObjectId to string

        # Ensure the response is a list of MinecraftCoordinate objects
        minecraft_coordinates = [MinecraftCoordinate(**coord) for coord in coordinates]

        return minecraft_coordinates  # Return a list of MinecraftCoordinate objects
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#listcoords: Retrieve all Minecraft coordinates for the current guild.
@coordinateRouter.get("/coordinates/{guild_name}", response_model=List[MinecraftCoordinate])
async def get_coordinates_by_guild(guild_name: str):
    """
    Retrieves all Minecraft coordinates stored in the database for a specific guild.
    """
    try:
        coordinates = MongoConnection.find_documents(DB_NAME, COLLECTION_NAME, {"guild_id": guild_name})

        print(f"📌 Database Response: {coordinates}")  #Debugging log

        if not coordinates:  
            return []  #Ensure a list is always returned

        minecraft_coordinates = [MinecraftCoordinate(**coord) for coord in coordinates]
        
        return minecraft_coordinates  #Always returns a List
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    
#find: Search for a Minecraft coordinate by its name.
@coordinateRouter.get("/coordinates/{coordinate_name}", response_model=MinecraftCoordinate)
async def find_coordinate(coordinate_name: str, guild_id: str = None):
    """
    Retrieves a Minecraft coordinate from the database by its name.
    """
    try:
        coordinate = MongoConnection.find_document(DB_NAME, COLLECTION_NAME, {"coordinateName": coordinate_name, "guild_id": guild_id})

        if not coordinate:
            raise HTTPException(status_code=404, detail="Coordinate not found")

        return MinecraftCoordinate(**coordinate)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#addcoord: Add a new Minecraft coordinate to the database.
@coordinateRouter.post("/coordinates/{guild_id}/{coordinate_name}", response_model=MinecraftCoordinate)
async def add_coordinate(guild_id: str, coordinate_name: str, coordinate: MinecraftCoordinate):
    """
    Adds a new Minecraft coordinate to the database.
    """
    try:
        coordinate.guild_id = guild_id
        coordinate.coordinateName = coordinate_name
        # Insert Coordinate Details into the database
        MongoConnection.insert_document(DB_NAME, COLLECTION_NAME, coordinate.dict())
        return coordinate
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#deletecoord: Delete a Minecraft coordinate by its name.
@coordinateRouter.delete("/coordinates/{guild_id}/{coordinate_name}")
async def delete_coordinate(guild_id: str, coordinate_name: str):
    """
    Deletes a Minecraft coordinate from the database by its guild_id and coordinate name.
    """
    try:
        deleted_count = MongoConnection.delete_document(
            DB_NAME, COLLECTION_NAME, {"guild_id": guild_id, "coordinateName": coordinate_name}
        )

        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="Coordinate not found")

        return {"message": "Coordinate deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#clearcoords: Clear all Minecraft coordinates for the current guild.
@coordinateRouter.delete("/coordinates/{guild_id}")
async def clear_coordinates(guild_id: str):
    """
    Deletes all Minecraft coordinates from the database for a specific guild.
    """
    try:
        result = MongoConnection.clear_documents(DB_NAME, COLLECTION_NAME, {"guild_id": guild_id})  # ✅ Pass filter query

        if result.deleted_count == 0:
            return {"message": "No coordinates found for this guild, nothing to delete"}

        return {"message": f"Deleted {result.deleted_count} coordinates successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    
    
#updateName (name): Update the name of an already saved coordinate.
#updateCoord (name): Update the coordinates of an already saved coordinate.

    


