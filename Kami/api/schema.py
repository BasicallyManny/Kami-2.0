from pydantic import BaseModel

class MinecraftCoordinate(BaseModel):
    guild_id: int
    channel_id: int
    user_id: int
    x: int
    y: int
    z: int
    description: str
