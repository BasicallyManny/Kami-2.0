from pydantic import BaseModel
from typing import Optional

# Model for Discord server data
class Server(BaseModel):
    _id: str
    guild_id: str  # Guild ID as string for consistency with Discord API
    channel_id: str
    logging_channel_id: Optional[str] = None  # Logging channel ID is optional

