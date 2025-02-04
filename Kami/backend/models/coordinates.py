from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional

# Enum to define allowed dimensions in Minecraft coordinates
class DimensionEnum(str, Enum):
    OVERWORLD = "overworld"
    NETHER = "nether"
    END = "end"

# Pydantic model for coordinate details (coordinates are now a nested object)
class CoordinateDetails(BaseModel):
    x: int
    y: int
    z: int

# Pydantic model for Minecraft coordinate data
class MinecraftCoordinate(BaseModel):
    """Pydantic model for Minecraft coordinate data."""
    _id: str
    guild_id: str  # Guild ID should be a string for Discord integration
    guild_name:str
    channel_id: str  # Channel ID as string for consistency with Discord API
    user_id: str  # User ID as string for consistency with Discord API
    username: str
    avatar_url: Optional[str] = None  # Avatar URL is optional
    coordinateName:str
    coordinates: CoordinateDetails
    dimension: DimensionEnum  # Use the DimensionEnum for Minecraft dimensions
    description: Optional[str] = None  # Description is optional
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())  # Automatically set the current time

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
