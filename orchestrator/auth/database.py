"""
User storage for authentication.

Schema:
  id               TEXT  — UUID, primary key
  email            TEXT  — unique, used to look up users at login
  hashed_password  TEXT  — bcrypt hash, never the plaintext
  created_at       TEXT  — ISO datetime string
"""

import os
import sqlite3
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

_DB_PATH = os.getenv("USERS_DB_PATH", "./data/users.db")


def get_connection() -> sqlite3.Connection:
    """Open the users DB, creating the file and table if they don't exist."""
    db_path = Path(_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    _ensure_table(conn)
    return conn


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id               TEXT PRIMARY KEY,
            email            TEXT UNIQUE NOT NULL,
            hashed_password  TEXT NOT NULL,
            created_at       TEXT NOT NULL
        )
    """)
    conn.commit()


def create_user(email: str, hashed_password: str) -> dict:
    """
    Insert a new user and return the created user dict.
    Raises sqlite3.IntegrityError if the email already exists —
    routes.py catches this and returns a 409 Conflict.
    """
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (id, email, hashed_password, created_at) VALUES (?, ?, ?, ?)",
            (user_id, email, hashed_password, now),
        )
        conn.commit()
        return {"id": user_id, "email": email, "created_at": now}
    finally:
        conn.close()


def get_user_by_email(email: str) -> dict | None:
    """Look up a user by email. Returns None if not found."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, email, hashed_password, created_at FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: str) -> dict | None:
    """Look up a user by ID. Used when the JWT is verified on each request."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, email, created_at FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
