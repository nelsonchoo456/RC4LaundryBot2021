from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.connectors import Connector

from api.auth import validate_api_key
from api.db.db import get_db


async def verify_api_key(
    x_api_key: str = Header(..., description="A valid API token."),
    c: Connector = Depends(get_db),
):
    if not validate_api_key(c, x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-KEY header is invalid",
        )

    return x_api_key
