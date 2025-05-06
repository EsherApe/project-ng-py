from typing import List, Optional
import secrets
from pydantic import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Project API"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite:///./project.db"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:4200",  # Angular frontend
        "http://localhost:8080",  # Development frontend
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
