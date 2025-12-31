from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    DB_ECHO: bool = True

    model_config = ConfigDict(env_file=".env")

settings = Settings()