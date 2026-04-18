"""
FastAPI dependency for authenticated routes.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from .jwt import decode_access_token
from .database import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Verify the JWT and return the authenticated user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user_id = decode_access_token(token)
    except JWTError:
        raise credentials_exception

    user = get_user_by_id(user_id)
    if user is None:
        # Token was valid but the user was deleted
        raise credentials_exception

    return user
