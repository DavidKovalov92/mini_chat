from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    DB_ECHO: bool = True
    
    JWT_SECRET_KEY: str = "your_default_secret_key"
    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 

    model_config = ConfigDict(env_file=".env")

settings = Settings()