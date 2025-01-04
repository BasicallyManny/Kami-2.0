from pydantic import BaseModel, Field # type: ignore
from datetime import datetime


class MinecraftCoordinate(BaseModel):
    guild_id: int
    channel_id: int
    user_id: int
    name:str
    x: int
    y: int
    z: int
    dimension: str
    created_at: datetime = Field(default_factory=datetime.now)  # Auto-filled timestamp

