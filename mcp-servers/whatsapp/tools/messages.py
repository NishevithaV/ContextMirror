"""
MCP tools for raw message access.

These are the tools the orchestrator calls to fetch WhatsApp data.
Each function decorated with @mcp.tool() becomes a callable tool
in the MCP protocol — the orchestrator discovers them via list_tools()
and calls them via call_tool(name, args).

The return type is always a JSON-serializable dict. FastMCP handles
converting it to the MCP content block format automatically.
"""

import json
from mcp.server.fastmcp import FastMCP

from ..db.connection import get_connection
from ..db import queries


def register_message_tools(mcp: FastMCP) -> None:
    """
    Register all message-related tools onto the FastMCP instance.

    We use a registration function instead of decorating at module level
    so that the mcp instance (created in server.py) is shared cleanly.
    """

    @mcp.tool()
    def get_chat_list() -> str:
        """
        List all WhatsApp chats the user has, sorted by most recent activity.
        Returns a JSON array of { jid, name, last_message_time }.
        """
        conn = get_connection()
        try:
            chats = queries.get_chats(conn)
            return json.dumps({"chats": chats})
        finally:
            conn.close()

    @mcp.tool()
    def search_contacts(query: str) -> str:
        """
        Search for contacts/chats by name. Case-insensitive partial match.

        Args:
            query: the name to search for, e.g. "Alice" or "fam"
        """
        conn = get_connection()
        try:
            results = queries.search_contacts(conn, query)
            return json.dumps({"contacts": results})
        finally:
            conn.close()

    @mcp.tool()
    def list_messages(
        chat_jid: str,
        limit: int = 100,
        start: str | None = None,
        end: str | None = None,
    ) -> str:
        """
        Fetch recent messages from a specific chat.

        Args:
            chat_jid: the WhatsApp JID for the chat (from get_chat_list)
            limit:    max number of messages to return (default 100)
            start:    optional start date filter, ISO format YYYY-MM-DD
            end:      optional end date filter, ISO format YYYY-MM-DD
        """
        conn = get_connection()
        try:
            messages = queries.get_messages(conn, chat_jid, limit, start, end)
            return json.dumps({"messages": messages, "count": len(messages)})
        finally:
            conn.close()

    @mcp.tool()
    def get_daily_summaries(start: str, end: str) -> str:
        """
        Return per-chat, per-day message counts for the given date range.

        This is the primary tool the orchestrator calls when building DayRecord
        objects — it maps directly onto the MessageSummary type in schema.json.

        Args:
            start: start date, YYYY-MM-DD
            end:   end date, YYYY-MM-DD

        Returns JSON shaped as:
          { summaries: [ { date, chat_jid, contact_name, message_count_sent,
                           message_count_received, active_hours } ] }
        """
        conn = get_connection()
        try:
            rows = queries.get_daily_message_counts(conn, start, end)

            summaries = []
            for row in rows:
                active_hours = queries.get_active_hours(
                    conn, row["chat_jid"], row["day"], row["day"]
                )
                summaries.append({
                    "date": row["day"],
                    "chat_id": row["chat_jid"],
                    "contact_name": row["chat_name"],
                    "message_count_sent": row["sent"],
                    "message_count_received": row["received"],
                    "active_hours": active_hours,
                })

            return json.dumps({"summaries": summaries})
        finally:
            conn.close()
