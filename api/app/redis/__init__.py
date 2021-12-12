from app.config import get_settings
from redis import ConnectionPool, Redis

settings = get_settings()
pool = ConnectionPool(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_pass,
)


def get_redis() -> Redis:
    """Fastapi dependency to get a redis client."""
    client = Redis(connection_pool=pool)
    yield client
    client.close()
