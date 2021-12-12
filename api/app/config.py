from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field, RedisDsn


class Settings(BaseSettings):
    api_key: str = Field(..., env="API_KEY")

    redis_host: str = Field(..., env="REDIS_HOST")
    redis_port: int = Field(..., env="REDIS_PORT")
    redis_db: int = Field(..., env="REDIS_DB")
    redis_pass: str = Field(..., env="REDIS_PASS")
    redis_test_url: RedisDsn = "redis://localhost:6380"

    dynamodb_url: Optional[str]
    dynamodb_region: str = Field(..., env="DYNAMODB_REGION")
    dynamodb_usage_table: str = Field(..., env="DYNAMODB_USAGE_TABLE")

    class Config:
        env_file = ".env.local"


@lru_cache()
def get_settings():
    return Settings()
