# Defines API endpoints that handle HTTP requests, validate input, and call MongoConnection methods.
from models.coordinates import MinecraftCoordinate
from config.connections import MongoConnection
from typing import List
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
        # Fetch the coordinates for the specified guild
        coordinates = MongoConnection.find_documents(DB_NAME, COLLECTION_NAME, {"guild_id": guild_name})

        if not coordinates:
            return {"message": f"No coordinates found for guild {guild_name}."}

        # Transform the documents to the MinecraftCoordinate model
        minecraft_coordinates = [MinecraftCoordinate(**coord) for coord in coordinates]

        return minecraft_coordinates  # Return the list of coordinates in the right format
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
#find: Search for a Minecraft coordinate by its name.
#updateName (name): Update the name of an already saved coordinate.
#updateCoord (name): Update the coordinates of an already saved coordinate.
    


