from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI()

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
                    <li><a href="/">Get All Coordinates (GET)</a></li>
                    <li><a href="/coordinates/{name}">Add Coordinate to Coordinates (POST)</a></li>
                    <li><a href="/coordinates/{name}">Delete Coordinate (DELETE)</a></li>
                </ul>
            </body>
        </html>
        """
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
