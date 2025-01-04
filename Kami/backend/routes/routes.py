from fastapi import APIRouter # type: ignore
from models.coordinates import MinecraftCoordinate
from schema.schemas import coordinates_serializer
from config.connections import MongoConnection
from typing import List

router = APIRouter()

#Access the mongo connection
def get_mongo_connection() -> MongoConnection:
    from app import mongo_connection
    return mongo_connection
