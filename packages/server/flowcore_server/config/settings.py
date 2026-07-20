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
    
    # Database Settings
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/flowcore"
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    
settings = Settings()
