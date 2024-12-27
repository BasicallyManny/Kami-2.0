from fastapi import FastAPI, HTTPException, Query # type: ignore
from Kami.backend.config.connections import MongoConnection
from Kami.backend.models import MinecraftCoordinate
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
