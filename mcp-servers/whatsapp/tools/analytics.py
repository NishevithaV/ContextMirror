"""
MCP tools for behavioral analytics — the custom tools we add on top of
what lharries/whatsapp-mcp provides out of the box.

These are the tools that make ContextMirror interesting:
  - Not just "fetch my messages" but "what patterns exist in my messages?"

The orchestrator calls these when building PatternInsight objects.
The ML engine will eventually do heavier analysis, but these tools do
the first layer of aggregation directly in SQL — which is fast and
keeps the heavy lifting close to the data.
"""

import json
import statistics
from mcp.server.fastmcp import FastMCP

from ..db.connection import get_connection
from ..db import queries


def register_analytics_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    def get_messaging_frequency(start: str, end: str) -> str:
        """
        Return total messages sent per day across all chats for the date range.

        Useful for detecting spikes (unusually high social activity) and drops
        (withdrawal patterns). The ML engine uses this as a time series input.

        Args:
            start: start date, YYYY-MM-DD
            end:   end date, YYYY-MM-DD

        Returns JSON shaped as:
          { by_date: { "2025-01-15": { sent: 42, received: 38 }, ... } }
        """
        conn = get_connection()
        try:
            rows = queries.get_daily_message_counts(conn, start, end)

            # Aggregate across all chats into a single count per day
            by_date: dict[str, dict] = {}
            for row in rows:
                day = row["day"]
                if day not in by_date:
                    by_date[day] = {"sent": 0, "received": 0}
                by_date[day]["sent"] += row["sent"]
                by_date[day]["received"] += row["received"]

            return json.dumps({"by_date": by_date})
        finally:
            conn.close()

    @mcp.tool()
    def get_active_hours_summary(start: str, end: str) -> str:
        """
        Return a histogram of what hours of the day the user sends messages,
        aggregated across all chats and the full date range.

        Example output: hour 23 has count 150 → user often messages late at night.
        The ML engine correlates this with sleep data from the Health MCP server.

        Args:
            start: start date, YYYY-MM-DD
            end:   end date, YYYY-MM-DD

        Returns JSON shaped as:
          { histogram: [ { hour: 0, count: 5 }, ..., { hour: 23, count: 150 } ] }
        """
        conn = get_connection()
        try:
            rows = conn.execute("""
                SELECT
                    CAST(strftime('%H', datetime(timestamp, 'unixepoch')) AS INTEGER) AS hour,
                    COUNT(*) AS count
                FROM messages
                WHERE is_from_me = 1
                  AND date(timestamp, 'unixepoch') BETWEEN ? AND ?
                GROUP BY hour
                ORDER BY hour
            """, (start, end)).fetchall()

            # Fill in zeros for hours with no activity so the histogram is complete
            counts = {row["hour"]: row["count"] for row in rows}
            histogram = [
                {"hour": h, "count": counts.get(h, 0)} for h in range(24)
            ]

            return json.dumps({"histogram": histogram})
        finally:
            conn.close()

    @mcp.tool()
    def get_response_time_stats(
        chat_jid: str, start: str, end: str
    ) -> str:
        """
        Compute response time statistics for a specific chat in the date range.

        Response time = seconds between receiving a message and sending the next one.
        High average response times may correlate with low energy, high stress,
        or being in back-to-back meetings (visible in Calendar MCP data).

        Args:
            chat_jid: the WhatsApp JID for the chat
            start:    start date, YYYY-MM-DD
            end:      end date, YYYY-MM-DD

        Returns JSON shaped as:
          { avg_seconds, median_seconds, min_seconds, max_seconds, sample_size }
        """
        conn = get_connection()
        try:
            times = queries.get_response_times(conn, chat_jid, start, end)

            if not times:
                return json.dumps({
                    "avg_seconds": None,
                    "median_seconds": None,
                    "min_seconds": None,
                    "max_seconds": None,
                    "sample_size": 0,
                })

            return json.dumps({
                "avg_seconds": round(statistics.mean(times), 1),
                "median_seconds": round(statistics.median(times), 1),
                "min_seconds": round(min(times), 1),
                "max_seconds": round(max(times), 1),
                "sample_size": len(times),
            })
        finally:
            conn.close()

    @mcp.tool()
    def get_top_contacts(start: str, end: str, limit: int = 10) -> str:
        """
        Return the contacts the user exchanges the most messages with
        in the given date range, ranked by total volume.

        Useful for understanding who the user's social energy is directed toward
        and whether that shifts during high-stress or low-sleep periods.

        Args:
            start: start date, YYYY-MM-DD
            end:   end date, YYYY-MM-DD
            limit: number of top contacts to return (default 10)
        """
        conn = get_connection()
        try:
            rows = conn.execute("""
                SELECT
                    m.chat_jid,
                    c.name AS contact_name,
                    SUM(CASE WHEN m.is_from_me = 1 THEN 1 ELSE 0 END) AS sent,
                    SUM(CASE WHEN m.is_from_me = 0 THEN 1 ELSE 0 END) AS received,
                    COUNT(*) AS total
                FROM messages m
                LEFT JOIN chats c ON c.jid = m.chat_jid
                WHERE date(m.timestamp, 'unixepoch') BETWEEN ? AND ?
                GROUP BY m.chat_jid
                ORDER BY total DESC
                LIMIT ?
            """, (start, end, limit)).fetchall()

            return json.dumps({"contacts": [dict(row) for row in rows]})
        finally:
            conn.close()
