from pydantic import BaseModel # type: ignore

class MinecraftCoordinate(BaseModel):
    guild_id: int
    channel_id: int
    user_id: int
    name:str
    x: int
    y: int
    z: int
    dimension: str
