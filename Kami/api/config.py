from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Discord Bot API"
    version: str = "1.0.0"

settings = Settings()