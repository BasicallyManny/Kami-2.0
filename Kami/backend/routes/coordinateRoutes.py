# Defines API endpoints that handle HTTP requests, validate input, and call MongoConnection methods.
from models.coordinates import MinecraftCoordinate
from config.connections import MongoConnection
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException # type: ignore
from datetime import datetime



# Create fastAPI router
router = APIRouter()
DB_NAME = "minecraft_db"
COLLECTION_NAME = "coordinates"

# ROUTE METHODS
@router.get("/coordinates/{guild_name}", response_model=List[MinecraftCoordinate])
async def get_all_coordinates(guild_name: str):
    try:
        return MongoConnection().find_document(DB_NAME, COLLECTION_NAME, {"guild_id": guild_name})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

