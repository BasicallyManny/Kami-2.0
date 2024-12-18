from fastapi import FastAPI, HTTPException, Query # type: ignore
from database.connections import MongoConnection
from api.schema import MinecraftCoordinate
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
MongoURI = os.getenv("mongoConnectionString")

# Initialize FastAPI
app = FastAPI()
mongo_connection = MongoConnection(MongoURI)

@app.on_event("startup")
async def startup_event():
    mongo_connection.connect()

@app.on_event("shutdown")
async def shutdown_event():
    mongo_connection.disconnect()

@app.get("/")
async def root():
    return {"message": "Welcome to the Minecraft Assistant API!"}

@app.post("/coordinates/")
async def save_coordinates(coordinate: MinecraftCoordinate):
    collection = mongo_connection.client.discord_bot.coordinates
    result = collection.insert_one(coordinate.dict())
    return {"message": "Coordinate saved successfully", "id": str(result.inserted_id)}

@app.get("/coordinates/")
async def get_coordinates(guild_id: int = Query(...)):
    collection = mongo_connection.client.discord_bot.coordinates
    coordinates = list(collection.find({"guild_id": guild_id}))
    for coord in coordinates:
        coord["_id"] = str(coord["_id"])
    return coordinates

@app.delete("/coordinates/{coord_id}")
async def delete_coordinate(coord_id: str):
    collection = mongo_connection.client.discord_bot.coordinates
    result = collection.delete_one({"_id": coord_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Coordinate not found.")
    return {"message": "Coordinate deleted successfully"}
