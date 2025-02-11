from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CoordinateDetails(BaseModel):
    x: int
    y: int
    z: int

# Add PyObjectId for proper BSON ObjectID handling
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class MinecraftCoordinate(BaseModel):
    """Pydantic model for Minecraft coordinate data."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    guild_id: str
    guild_name: str
    channel_id: str
    user_id: str
    username: str
    avatar_url: Optional[str] = None
    coordinateName: str
    coordinates: CoordinateDetails
    dimension: str
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
        allow_population_by_field_name = True