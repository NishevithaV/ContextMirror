"""
SQL queries against the WhatsApp SQLite database.

The lharries/whatsapp-bridge creates these tables:
  messages  — one row per message (id, chat_jid, sender, text, timestamp, is_from_me)
  chats     — one row per chat (jid, name, last_message_time)

We never write. All functions take a connection and return plain dicts/lists
so the tool layer can serialize them however it wants.

Raw SQL used instead of an ORM (object relational mapper) as the db is owned 
by the Go bridge, and the app is a read-only consumer. Raw SQL is faster without
overhead of an ORM layer. 
"""

import sqlite3
from datetime import date


def get_chats(conn: sqlite3.Connection) -> list[dict]:
    """All chats the user has, sorted by most recent activity."""
    rows = conn.execute("""
        SELECT jid, name, last_message_time
        FROM chats
        ORDER BY last_message_time DESC
    """).fetchall()
    return [dict(row) for row in rows]


def search_contacts(conn: sqlite3.Connection, query: str) -> list[dict]:
    """Search chats by name. Case-insensitive LIKE match."""
    rows = conn.execute("""
        SELECT jid, name, last_message_time
        FROM chats
        WHERE name LIKE ?
        ORDER BY last_message_time DESC
        LIMIT 20
    """, (f"%{query}%",)).fetchall()
    return [dict(row) for row in rows]


def get_messages(
    conn: sqlite3.Connection,
    chat_jid: str,
    limit: int = 100,
    start: str | None = None,
    end: str | None = None,
) -> list[dict]:
    """
    Fetch messages for a specific chat, optionally filtered by date range.

    timestamp is a Unix epoch integer in the bridge DB.
    We convert to ISO datetime string for easier consumption upstream.
    """
    sql = """
        SELECT
            id,
            chat_jid,
            sender,
            text,
            datetime(timestamp, 'unixepoch') AS sent_at,
            is_from_me
        FROM messages
        WHERE chat_jid = ?
    """
    params: list = [chat_jid]

    if start:
        sql += " AND datetime(timestamp, 'unixepoch', 'localtime') >= ?"
        params.append(start)
    if end:
        sql += " AND datetime(timestamp, 'unixepoch', 'localtime') <= ?"
        params.append(end)

    sql += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def get_daily_message_counts(
    conn: sqlite3.Connection,
    start: str,
    end: str,
) -> list[dict]:
    """
    Aggregate message counts per chat per day.

    Returns rows shaped like:
      { date, chat_jid, chat_name, sent, received }

    This is what get_daily_summaries in tools/messages.py uses to build
    MessageSummary objects that match shared/schema.json.
    """
    rows = conn.execute("""
        SELECT
            date(m.timestamp, 'unixepoch') AS day,
            m.chat_jid,
            c.name AS chat_name,
            SUM(CASE WHEN m.is_from_me = 1 THEN 1 ELSE 0 END) AS sent,
            SUM(CASE WHEN m.is_from_me = 0 THEN 1 ELSE 0 END) AS received
        FROM messages m
        LEFT JOIN chats c ON c.jid = m.chat_jid
        WHERE date(m.timestamp, 'unixepoch') BETWEEN ? AND ?
        GROUP BY day, m.chat_jid
        ORDER BY day, sent DESC
    """, (start, end)).fetchall()
    return [dict(row) for row in rows]


def get_active_hours(
    conn: sqlite3.Connection,
    chat_jid: str,
    start: str,
    end: str,
) -> list[int]:
    """
    Which hours of the day did the user send messages in a given chat?

    Returns a list of hour integers (0-23), deduplicated, sorted.
    Used for the active_hours field in MessageSummary.
    """
    rows = conn.execute("""
        SELECT DISTINCT
            CAST(strftime('%H', datetime(timestamp, 'unixepoch')) AS INTEGER) AS hour
        FROM messages
        WHERE chat_jid = ?
          AND is_from_me = 1
          AND date(timestamp, 'unixepoch') BETWEEN ? AND ?
        ORDER BY hour
    """, (chat_jid, start, end)).fetchall()
    return [row["hour"] for row in rows]


def get_response_times(
    conn: sqlite3.Connection,
    chat_jid: str,
    start: str,
    end: str,
) -> list[float]:
    """
    Compute response times in seconds: time between receiving a message
    and sending the next one in the same chat.

    Strategy: for each outgoing message, find the most recent incoming
    message before it and compute the gap. This is an approximation —
    it doesn't account for multi-message conversations perfectly, but
    it's good enough for trend analysis.
    """
    rows = conn.execute("""
        SELECT
            m_out.timestamp AS replied_at,
            MAX(m_in.timestamp) AS received_at
        FROM messages m_out
        JOIN messages m_in
          ON m_in.chat_jid = m_out.chat_jid
         AND m_in.is_from_me = 0
         AND m_in.timestamp < m_out.timestamp
        WHERE m_out.chat_jid = ?
          AND m_out.is_from_me = 1
          AND date(m_out.timestamp, 'unixepoch') BETWEEN ? AND ?
        GROUP BY m_out.id
        HAVING (m_out.timestamp - MAX(m_in.timestamp)) < 86400  -- ignore >1 day gaps
    """, (chat_jid, start, end)).fetchall()

    return [float(row["replied_at"] - row["received_at"]) for row in rows]
