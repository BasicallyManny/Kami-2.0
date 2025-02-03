# Defines API endpoints that handle HTTP requests, validate input, and call MongoConnection methods.
from models.coordinates import MinecraftCoordinate
from schema.schemas import coordinates_serializer
from config.connections import MongoConnection
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException # type: ignore
from datetime import datetime



# Create fastAPI router
router = APIRouter()
DB_NAME = "minecraft_db"
COLLECTION_NAME = "coordinates"

# ROUTE METHODS


