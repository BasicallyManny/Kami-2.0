from pydantic import BaseModel, Field  # Correct: Using Field for extra metadata
from datetime import datetime
from enum import Enum

# Enum to define allowed dimensions in Minecraft coordinates
class DimensionEnum(str, Enum):
    OVERWORLD = "overworld"
    NETHER = "nether"
    END = "end"

# Pydantic model for Minecraft coordinate data
class MinecraftCoordinate(BaseModel):
    """Pydantic model for Minecraft coordinate data."""
    guild_id: int
    channel_id: int
    user_id: int 
    name: str
    x: int
    y: int
    z: int
    dimension: DimensionEnum  # Use the DimensionEnum for Minecraft dimensions
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())  # Field with default UTC time
