"""
SQLite connection for the WhatsApp MCP server.

The Go bridge (whatsapp-bridge from lharries/whatsapp-mcp) writes all
WhatsApp messages into a SQLite database.

Python's built-in sqlite3 module used 

The DB path comes from an env var so it works both locally and in Docker:
  - Locally: point it at wherever the Go bridge writes its DB
  - Docker: mount the bridge's data volume and set WHATSAPP_DB_PATH
"""

import os
import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_DB_PATH = os.getenv("WHATSAPP_DB_PATH", "./data/whatsapp.db")


def get_connection() -> sqlite3.Connection:
    """
    Open a read-only SQLite connection.

    uri=True + ?mode=ro means we open the file in read-only mode at the
    OS level — SQLite won't let accidental write to the bridge's DB.

    row_factory=sqlite3.Row makes rows behave like dicts: row["column_name"]
    instead of row[0]. 
    """
    db_path = Path(_DB_PATH).resolve()

    if not db_path.exists():
        logger.warning(f"WhatsApp DB not found at {db_path}. Is the bridge running?")
        # Return an in-memory DB so the server starts even without the bridge.
        # All queries will return empty results rather than crashing.
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        return conn

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    logger.info(f"Connected to WhatsApp DB at {db_path}")
    return conn
