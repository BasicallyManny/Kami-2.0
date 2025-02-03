# Defines API endpoints that handle HTTP requests, validate input, and call MongoConnection methods.
from models.coordinates import MinecraftCoordinate
from schema.schemas import coordinates_serializer
from config.connections import MongoConnection
from typing import Dict, Any, List
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException # type: ignore
from datetime import datetime



# Load environment variables
load_dotenv()

# Initialize mongoDB connection
mongoConnection = MongoConnection("mongoConnectionString")
mongoConnection.connect()

# Create fastAPI router
router = APIRouter()

DB_NAME = "minecraft_db"
COLLECTION_NAME = "coordinates"

# GET Request Method

