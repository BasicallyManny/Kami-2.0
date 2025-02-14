# Defines API endpoints that handle HTTP requests, validate input, and call MongoConnection methods.
from models.coordinates import MinecraftCoordinate, CoordinateUpdatePayload
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
        coordinates = MongoConnection.find_documents(DB_NAME, COLLECTION_NAME, {"guild_id": guild_name})

        if not coordinates:  
            return []  #Ensure a list is always returned

        minecraft_coordinates = [MinecraftCoordinate(**coord) for coord in coordinates]
        
        return minecraft_coordinates  #Always returns a List
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    
#find: Search for a Minecraft coordinate by its name.
@coordinateRouter.get("/coordinates/{guild_id}/{coordinate_name}", response_model=List[MinecraftCoordinate])
async def get_coordinate(guild_id: str, coordinate_name: str):
    """Retrieves a Minecraft coordinate from the database by its name."""
    try:
        coordinates = MongoConnection.find_documents(
            DB_NAME, 
            COLLECTION_NAME, 
            {"guild_id": guild_id, "coordinateName": coordinate_name}
        )
        
        if not coordinates:
            raise HTTPException(status_code=404, detail="Coordinate Name not found")
        
        # The model will now handle the ObjectId conversion automatically
        response_data = [MinecraftCoordinate(**coord) for coord in coordinates]
        return response_data
        
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

#updatecoord: Update an existing Minecraft coordinate in the database.
@coordinateRouter.put("/coordinates/{guild_id}/{coordinate_name}", response_model=MinecraftCoordinate)
async def overwrite_coordinate(guild_id: str, coordinate_name: str, coordinate: MinecraftCoordinate):
    """
    Updates an existing Minecraft coordinate in the database.
    """
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
    
#updateCoord (name): Update the name coordinates of an already saved coordinate.
# Rename only: use PATCH for partial update
@coordinateRouter.patch("/coordinates/{guild_id}/{coordinate_name}", response_model=MinecraftCoordinate)
async def update_coordinate(
    guild_id: str,
    coordinate_name: str,
    update_data: CoordinateUpdatePayload
):
    """
    Update a coordinate's name and/or coordinates in the database.
    At least one of new_name or coordinates must be provided.
    Returns the updated MinecraftCoordinate document.
    """
    try:
        new_name = update_data.new_name
        coordinates = update_data.coordinates

        if not new_name and not coordinates:
            raise HTTPException(
                status_code=400,
                detail="Either new_name or coordinates must be provided"
            )

        # Fetch the existing coordinate
        existing = MongoConnection.find_one_document(
            DB_NAME, COLLECTION_NAME,
            {"coordinateName": coordinate_name, "guild_id": guild_id}
        )

        if not existing:
            raise HTTPException(status_code=404, detail="Coordinate not found")

        # If new name is provided, check for duplicates
        if new_name:
            name_exists = MongoConnection.find_one_document(
                DB_NAME, COLLECTION_NAME,
                {
                    "coordinateName": new_name,
                    "guild_id": guild_id,
                    "_id": {"$ne": existing["_id"]}  # Exclude current document
                }
            )

            if name_exists:
                raise HTTPException(
                    status_code=400,
                    detail=f"Coordinate name '{new_name}' already exists."
                )

        # Prepare update document
        update_fields = {}
        if coordinates:
            update_fields["coordinates"] = coordinates.dict()
        if new_name:
            update_fields["coordinateName"] = new_name

        # Update the document
        updated_doc = MongoConnection.update_and_return_document(
            DB_NAME,
            COLLECTION_NAME,
            {"coordinateName": coordinate_name, "guild_id": guild_id},
            update_fields
        )

        if not updated_doc:
            raise HTTPException(status_code=400, detail="Update failed. No changes made.")

        # Convert the MongoDB document to a Pydantic model
        return MinecraftCoordinate(**updated_doc)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
        

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
    

    


