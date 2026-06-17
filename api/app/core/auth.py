from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
 
from app.core.config import get_settings
 
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
 
 
async def require_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """
    Dependency that validates the X-API-Key header against the configured key.
    Raises 401 if missing or 403 if invalid.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header is missing.",
        )
    if api_key != get_settings().api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )
    return api_key