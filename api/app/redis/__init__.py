from app.config import Settings, get_settings
from fastapi import Depends
from redis import Redis


def get_redis(settings: Settings = Depends(get_settings)) -> Redis:
    """Fastapi dependency to get a redis client."""
    client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_pass,
    )
    yield client
    client.close()
