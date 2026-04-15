"""
Pydantic models for the orchestrator.
These are the Python runtime equivalent of shared/schema.json.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# Enums

class EventStatus(str, Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"
    tentative = "tentative"


class InsightType(str, Enum):
    correlation = "correlation"  
    trend = "trend"              
    anomaly = "anomaly"           
    cluster = "cluster"           


class DataSource(str, Enum):
    health = "health"
    calendar = "calendar"
    messaging = "messaging"


# Sub-models 

class TimeRange(BaseModel):
    start: datetime
    end: datetime


class HealthMetrics(BaseModel):
    """A single day's health snapshot. Populated by the Health MCP server."""
    steps: int | None = Field(None, ge=0)
    sleep_hours: float | None = Field(None, ge=0, le=24)
    sleep_quality: float | None = Field(None, ge=0, le=10)
    heart_rate_avg: int | None = Field(None, ge=0)
    active_minutes: int | None = Field(None, ge=0)
    calories_burned: int | None = Field(None, ge=0)


class CalendarEvent(BaseModel):
    """A single calendar event. Populated by the Calendar MCP server."""
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    status: EventStatus
    category: str | None = None
    attendee_count: int | None = Field(None, ge=0)
    location: str | None = None


class MessageSummary(BaseModel):
    """
    Daily messaging summary per contact. Populated by the WhatsApp MCP server.
    One DayRecord can have many MessageSummary objects (one per active chat).
    """
    chat_id: str
    contact_name: str | None = None
    date: date
    message_count_sent: int = Field(0, ge=0)
    message_count_received: int = Field(0, ge=0)
    response_time_avg_seconds: float | None = Field(None, ge=0)
    active_hours: list[int] = Field(
        default_factory=list,
        description="Hours of the day (0-23) when messages were sent"
    )
    sentiment_score: float | None = Field(None, ge=-1, le=1)


# Top-level models 

class DayRecord(BaseModel):
    """
    The unified snapshot of a single day across ALL data sources.
    The orchestrator assembles this by calling all 3 MCP servers and merging
    their responses. This is the core data structure of the whole system.
    """
    date: date
    user_id: str
    health: HealthMetrics | None = None
    calendar_events: list[CalendarEvent] = Field(default_factory=list)
    messaging: list[MessageSummary] = Field(default_factory=list)


class PatternInsight(BaseModel):
    """
    A single pattern detected by the ML engine.
    """
    id: str
    type: InsightType
    description: str
    confidence: float = Field(..., ge=0, le=1)
    sources: list[DataSource]
    date_range: TimeRange | None = None
    supporting_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Raw numbers for charts — shape varies by insight type"
    )
    reflection_question: str | None = None


class InsightResponse(BaseModel):
    """
    The top-level response the orchestrator sends to the frontend.
    One call to GET /insights returns one of these.
    """
    user_id: str
    generated_at: datetime
    summary: str | None = None
    insights: list[PatternInsight] = Field(default_factory=list)
    timeline: list[DayRecord] = Field(default_factory=list)
