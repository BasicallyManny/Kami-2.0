from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class CoordinateDetails(BaseModel):
    """Represents Minecraft coordinate details."""
    x: int
    y: int
    z: int

# Custom ObjectId type for Pydantic v2
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, *args, **kwargs):
        from pydantic_core import core_schema

        return core_schema.chain_schema([
            core_schema.str_schema(),
            core_schema.no_info_plain_validator_function(cls.validate),
            core_schema.json_or_python_schema(
                json_schema=core_schema.str_schema(),
                python_schema=core_schema.no_info_plain_validator_function(cls.validate),
            ),
        ])

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class CoordinateUpdatePayload(BaseModel):
    """Model for updating Minecraft coordinate entries."""
    coordinateName: Optional[str] = Field(None, min_length=1, max_length=100)
    coordinates: Optional[CoordinateDetails] = None
    dimension: Optional[str] = None 


class MinecraftCoordinate(BaseModel):
    """Pydantic model for Minecraft coordinate data."""
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    guild_id: str
    guild_name: str
    channel_id: str
    user_id: str
    username: str
    avatar_url: Optional[str] = None
    coordinateName: str = Field(..., min_length=1, max_length=100)
    coordinates: CoordinateDetails
    dimension: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    )
