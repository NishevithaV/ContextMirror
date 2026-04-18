"""
JWT token creation and verification.
"""

import os
import logging
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

logger = logging.getLogger(__name__)

_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-production")
_ALGORITHM = "HS256"
_EXPIRY_DAYS = 7


def create_access_token(user_id: str) -> str:
    """
    Create a signed JWT containing the user's ID.

    'sub' (subject) is the standard JWT claim for who the token belongs to.
    'exp' (expiry) is checked automatically by python-jose on decode.
    """
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=_EXPIRY_DAYS),
    }
    return jwt.encode(payload, _SECRET_KEY, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> str:
    """
    Verify a JWT and return the user_id inside it.

    Raises JWTError if the token is invalid, expired, or tampered with.
    The caller (deps.py) catches this and returns a 401 Unauthorized.
    """
    payload = jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise JWTError("Token missing subject claim")
    return user_id
