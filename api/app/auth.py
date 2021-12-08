from app.config import Settings, get_settings
from fastapi import Depends, Header, HTTPException, status


def validate_api_key(
    x_api_key: str = Header(..., description="A valid API token."),
    settings: Settings = Depends(get_settings),
):
    """Dependency for validating a given api key."""
    if x_api_key != settings.api_key:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="X-API-KEY header is invalid."
        )
    return x_api_key
