from pydantic import BaseModel
from typing import Optional


class ChatResponse(BaseModel):
    answer: Optional[str] = None
    urls: Optional[list[str]] = None