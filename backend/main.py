import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.concurrency import asynccontextmanager
import logging
from rich.logging import RichHandler
from config.connections import MongoConnection
from dotenv import load_dotenv
#import routes
from routes.coordinateRoutes import coordinateRouter
from routes.botRoutes import chatbotRouter

# Load environment variables from .env file
load_dotenv()
mongoConnectionString = os.getenv("mongoConnectionString")
# Initialize MongoDB connection with the URI loaded from environment variables
mongoConnection = MongoConnection(mongoConnectionString)  # Update this URI to your MongoDB connection string
# Lifespan context manager for handling MongoDB connection at startup and shutdown
#set up logger
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)

logger = logging.getLogger("uvicorn.error")  # Uses uvicorn's logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle MongoDB connection at startup and shutdown."""
    try:
        mongoConnection.connect()  # Connect to MongoDB
        logger.info("Connected to MongoDB (main)")
        yield
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise e
    finally:
        logger.info("Disconnecting from MongoDB...")
        mongoConnection.disconnect()  # Disconnect from MongoDB

# Initialize FastAPI app and register lifespan context manager
app = FastAPI(lifespan=lifespan)
app.include_router(coordinateRouter)
app.include_router(chatbotRouter, tags=["Chatbot"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Path to your static HTML file
    file_path = os.path.join(os.getcwd(), "static", "index.html")
    with open(file_path, "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

