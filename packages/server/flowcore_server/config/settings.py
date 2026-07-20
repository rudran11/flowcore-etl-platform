from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    """
    Application Settings
    """
    model_config = SettingsConfigDict(env_prefix="FLOWCORE_", env_file=".env", env_file_encoding="utf-8")
    
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "dev"
    cors_origins: List[str] = ["*"]
    
settings = Settings()
