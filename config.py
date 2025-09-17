from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    baileys_api_url: str = "http://chatbot.auto-atendimento.digital:3001"
    frontend_url: str = "http://chatbot.auto-atendimento.digital:8000"
    
    class Config:
        env_file = ".env"

settings = Settings()
