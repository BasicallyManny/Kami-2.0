from fastapi import FastAPI, HTTPException, Query # type: ignore
from backend.routes.routes import router as CoordinatesRouter


app = FastAPI()

# Include the router for coordinate endpoints
app.include_router(CoordinatesRouter, prefix="/coordinates")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Minecraft Coordinate API is running!"}



