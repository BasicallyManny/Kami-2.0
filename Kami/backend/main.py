import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.concurrency import asynccontextmanager

from config.connections import MongoConnection
from dotenv import load_dotenv
#import routes
from routes.coordinateRoutes import coordinateRouter

# Load environment variables from .env file
load_dotenv()
mongoConnectionString = os.getenv("mongoConnectionString")
# Initialize MongoDB connection with the URI loaded from environment variables
mongoConnection = MongoConnection(mongoConnectionString)  # Update this URI to your MongoDB connection string
# Lifespan context manager for handling MongoDB connection at startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle MongoDB connection at startup and shutdown."""
    try:
        mongoConnection.connect()  # Connect to MongoDB
        print("Connected to MongoDB (main)")
        yield
    except Exception as e:
        print(f"Error during lifespan: {e}")
        raise e
    finally:
        print("Disconnecting MongoDB...")
        mongoConnection.disconnect()  # Disconnect from MongoDB

# Initialize FastAPI app and register lifespan context manager
app = FastAPI(lifespan=lifespan)
# ✅ Register the router (this adds all routes from routes.py)
app.include_router(coordinateRouter)

@app.get("/", response_class=HTMLResponse, tags=["Home"])
async def root():
    """
    Retrieves all Minecraft coordinates stored in the database and returns them as clickable HTML links.
    Includes links to all available CRUD operations and the API documentation.
    """
    try:
        return """
        <html>
            <head>
                <title>API Routes</title>
            </head>
            <body>
                <h1>List of all available routes:</h1>
                <ul>
                    <li><a href="/openapi.json">OpenAPI Schema</a></li>
                    <li><a href="/docs">Swagger UI Docs</a></li>
                    <li><a href="/coordinates">Get All Coordinates (GET)</a></li>
                    <li><a href="/coordinates/{name}">Add Coordinate to Coordinates (POST)</a></li>
                    <li><a href="/coordinates/{name}">Delete Coordinate (DELETE)</a></li>
                </ul>
            </body>
        </html>
        """
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

