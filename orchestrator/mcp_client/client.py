"""
MCP Client — the orchestrator's connection layer to all 3 MCP servers.

How MCP works at the transport level:
  - Each MCP server listens for SSE connections on a /sse endpoint.
  - SSE (Server-Sent Events) is a one-directional HTTP stream: server → client.
  - For client → server messages, there's a separate HTTP POST endpoint (/messages).

The flow for a single tool call:
  1. We open an SSE connection to the server (long-lived HTTP GET)
  2. We POST a JSON-RPC "tools/call" request to /messages
  3. The server streams the response back over the SSE connection
  4. The SDK handles all of this; we just call session.call_tool()

  We manage connections at app startup rather than per-request because:
  - Opening an SSE connection has overhead (TCP + HTTP handshake).
  - If we opened a new connection for every /insights request, the latency
    would stack up. Instead we keep connections alive and reuse them.
"""

import json
import logging
import os
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.sse import sse_client

from .models import (
    CalendarEvent,
    DayRecord,
    EventStatus,
    HealthMetrics,
    MessageSummary,
)

logger = logging.getLogger(__name__)


class MCPClient:
    """
    Manages persistent SSE connections to all 3 MCP servers and exposes
    high-level methods that return typed Python objects.
    """

    def __init__(self) -> None:
        self.calendar_url = os.getenv("CALENDAR_MCP_URL", "http://localhost:3001")
        self.whatsapp_url = os.getenv("WHATSAPP_MCP_URL", "http://localhost:3002")
        self.health_url = os.getenv("HEALTH_MCP_URL", "http://localhost:3003")

        # Sessions are None until connect() is called.
        self._calendar_session: ClientSession | None = None
        self._whatsapp_session: ClientSession | None = None
        self._health_session: ClientSession | None = None

        # AsyncExitStack allows to manage multiple async context managers
        # (the SSE connections) and tear them all down cleanly on disconnect.
        self._exit_stack = AsyncExitStack()

    async def connect(self) -> None:
        """
        Open SSE connections to all 3 MCP servers and run the MCP handshake.

        The handshake (session.initialize()) exchanges protocol versions and
        capabilities. Client learns what tools the server supports.
        Log available tools here so it's visible in startup logs.
        """
        logger.info("Connecting to MCP servers...")

        self._calendar_session = await self._open_session(
            self.calendar_url, "calendar-mcp"
        )
        self._whatsapp_session = await self._open_session(
            self.whatsapp_url, "whatsapp-mcp"
        )
        self._health_session = await self._open_session(
            self.health_url, "health-mcp"
        )

        logger.info("All MCP servers connected.")

    async def disconnect(self) -> None:
        """Close all SSE connections gracefully."""
        await self._exit_stack.aclose()
        logger.info("MCP connections closed.")

    async def _open_session(self, base_url: str, name: str) -> ClientSession:
        """
        Open a single SSE connection and return an initialized ClientSession.

        sse_client() is an async context manager that yields (read_stream, write_stream).
        We enter it via the exit_stack so it stays open until disconnect() is called.
        """
        sse_url = f"{base_url}/sse"
        try:
            read, write = await self._exit_stack.enter_async_context(
                sse_client(sse_url)
            )
            session = await self._exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            logger.info(f"{name} connected. Tools available: {tool_names}")

            return session
        except Exception as e:
            logger.warning(f"Could not connect to {name} at {sse_url}: {e}")
            # Return None-like — callers check for None before using sessions.
            # This lets the orchestrator start up even if one server is down.
            raise


    # These methods call the raw MCP tools and return typed Python objects.
    # The orchestrator's route handlers call these — they never touch the MCP
    # protocol directly.

    async def fetch_day_records(
        self, user_id: str, start: str, end: str
    ) -> list[DayRecord]:
        """
        Fetch data from all 3 MCP servers in parallel and merge into DayRecord[].

        asyncio.gather() runs all 3 calls concurrently. 
        """
        import asyncio

        calendar_task = self._fetch_calendar_events(start, end)
        whatsapp_task = self._fetch_messaging_summaries(start, end)
        health_task = self._fetch_health_metrics(start, end)

        calendar_events, messaging, health_by_date = await asyncio.gather(
            calendar_task, whatsapp_task, health_task,
            return_exceptions=True,  
        )

        # Build a dict keyed by date string to merge all 3 streams.
        records: dict[str, DayRecord] = {}

        def get_or_create(d: str) -> DayRecord:
            if d not in records:
                records[d] = DayRecord(date=d, user_id=user_id)
            return records[d]

        if isinstance(calendar_events, list):
            for event in calendar_events:
                record = get_or_create(event.start_time.date().isoformat())
                record.calendar_events.append(event)

        if isinstance(messaging, list):
            for summary in messaging:
                record = get_or_create(summary.date.isoformat())
                record.messaging.append(summary)

        if isinstance(health_by_date, dict):
            for date_str, metrics in health_by_date.items():
                get_or_create(date_str).health = metrics

        return sorted(records.values(), key=lambda r: r.date)

    # Private tool callers

    async def _fetch_calendar_events(
        self, start: str, end: str
    ) -> list[CalendarEvent]:
        if self._calendar_session is None:
            return []

        result = await self._calendar_session.call_tool(
            "list_events", {"start": start, "end": end}
        )
        raw = self._parse_tool_result(result)
        return [CalendarEvent(**e) for e in raw.get("events", [])]

    async def _fetch_messaging_summaries(
        self, start: str, end: str
    ) -> list[MessageSummary]:
        if self._whatsapp_session is None:
            return []

        result = await self._whatsapp_session.call_tool(
            "get_daily_summaries", {"start": start, "end": end}
        )
        raw = self._parse_tool_result(result)
        return [MessageSummary(**s) for s in raw.get("summaries", [])]

    async def _fetch_health_metrics(
        self, start: str, end: str
    ) -> dict[str, HealthMetrics]:
        """
        Fetch daily health metrics from the Momentum Apple Health MCP server.

        The health MCP server (mcp-servers/health) exposes tools from
        DuckDB-backed Apple Health data.  We call get_trend_data_duckdb once
        per metric type with interval="day" to get daily averages, then merge
        all metric streams into a {date: HealthMetrics} dict.

        HK type → HealthMetrics field mapping:
          HKQuantityTypeIdentifierStepCount         → steps
          HKCategoryTypeIdentifierSleepAnalysis     → sleep_hours  (value in hours)
          HKQuantityTypeIdentifierHeartRate         → heart_rate_avg
          HKQuantityTypeIdentifierActiveEnergyBurned → calories_burned
          HKQuantityTypeIdentifierAppleExerciseTime → active_minutes

        Tool contract (get_trend_data_duckdb):
          Returns: list[{
            "date": "YYYY-MM-DD",
            "avg_value": float,
            "total_value": float,
            "count": int
          }]
        """
        if self._health_session is None:
            return {}

        import asyncio

        # (hk_type, field_name, use_total_instead_of_avg)
        # Steps and calories are cumulative; heart rate and sleep are averages.
        metric_map: list[tuple[str, str, bool]] = [
            ("HKQuantityTypeIdentifierStepCount", "steps", True),
            ("HKCategoryTypeIdentifierSleepAnalysis", "sleep_hours", False),
            ("HKQuantityTypeIdentifierHeartRate", "heart_rate_avg", False),
            ("HKQuantityTypeIdentifierActiveEnergyBurned", "calories_burned", True),
            ("HKQuantityTypeIdentifierAppleExerciseTime", "active_minutes", True),
        ]

        async def fetch_one(hk_type: str, use_total: bool) -> list[dict]:
            try:
                result = await self._health_session.call_tool(
                    "get_trend_data_duckdb",
                    {
                        "record_type": hk_type,
                        "interval": "day",
                        "date_from": start,
                        "date_to": end,
                    },
                )
                # get_trend_data_duckdb returns a JSON list directly in text
                import json as _json
                content = result.content
                if content and content[0].type == "text":
                    rows = _json.loads(content[0].text)
                    return rows if isinstance(rows, list) else []
                return []
            except Exception as exc:
                logger.warning("Health MCP fetch failed for %s: %s", hk_type, exc)
                return []

        # Fire all 5 metric fetches concurrently
        fetch_tasks = [fetch_one(hk_type, use_total) for hk_type, _, use_total in metric_map]
        all_rows = await asyncio.gather(*fetch_tasks)

        # Merge into {date: HealthMetrics}
        by_date: dict[str, dict] = {}
        for (hk_type, field_name, use_total), rows in zip(metric_map, all_rows):
            for row in rows:
                date_str = row.get("date", "")
                if not date_str:
                    continue
                # Normalise to YYYY-MM-DD (DuckDB may return full timestamp)
                date_str = str(date_str)[:10]
                if date_str not in by_date:
                    by_date[date_str] = {}
                value = row.get("total_value" if use_total else "avg_value")
                if value is not None:
                    by_date[date_str][field_name] = round(float(value), 2)

        return {date_str: HealthMetrics(**fields) for date_str, fields in by_date.items()}

    @staticmethod
    def _parse_tool_result(result) -> dict:
        """
        MCP tool results come back as a list of content blocks.
        Each block has a 'type' ('text') and 'text' (JSON string).
        """
        if result.content and result.content[0].type == "text":
            return json.loads(result.content[0].text)
        return {}
