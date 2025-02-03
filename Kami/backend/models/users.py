from pydantic import BaseModel

class User(BaseModel):
    _id : str
    username: str
    user_id: str
    avatar_url: str
    joined_servers: list
    