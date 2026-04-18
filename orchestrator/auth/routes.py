"""
Auth endpoints for register and login.
"""

import sqlite3
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, HTTPException, status
from passlib.context import CryptContext

from .database import create_user, get_user_by_email
from .jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Request / Response models 
class AuthRequest(BaseModel):
    email: EmailStr   
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str


# Routes 
@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: AuthRequest):
    """
    Create a new account and return a JWT.

    Password is hashed with bcrypt before storage. Never see or store
    the plaintext. If the email is already taken, return 409 Conflict.
    """
    hashed = pwd_context.hash(body.password)

    try:
        user = create_user(email=body.email, hashed_password=hashed)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    token = create_access_token(user["id"])
    return TokenResponse(access_token=token, user_id=user["id"], email=user["email"])


@router.post("/login", response_model=TokenResponse)
async def login(body: AuthRequest):
    """
    Verify credentials and return a JWT.
    """
    user = get_user_by_email(body.email)

    if user is None or not pwd_context.verify(body.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(user["id"])
    return TokenResponse(access_token=token, user_id=user["id"], email=user["email"])
