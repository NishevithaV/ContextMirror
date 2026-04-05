"""
REST API routes — what the frontenda calls.
"""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.requests import Request

from ..mcp_client.models import DayRecord, InsightResponse, PatternInsight

router = APIRouter(prefix="/api/v1")


# Dependency: get the MCP client from app state 
# FastAPI's dependency injection system allows to declare shared
# resources that routes need. 

def get_mcp_client(request: Request):
    return request.app.state.mcp_client


# Routes 
@router.get("/health")
async def health_check():
    """Simple liveness check. Load balancers and Docker healthchecks call this."""
    return {"status": "ok"}


@router.get("/timeline", response_model=list[DayRecord])
async def get_timeline(
    user_id: str = Query(..., description="User identifier"),
    start: date = Query(
        default_factory=lambda: date.today() - timedelta(days=30),
        description="Start date (default: 30 days ago)",
    ),
    end: date = Query(
        default_factory=date.today,
        description="End date (default: today)",
    ),
    mcp_client=Depends(get_mcp_client),
):
    """
    Fetch the raw unified timeline for a user of one DayRecord per day.

    The frontend uses this to render the scrollable timeline view.
    Each DayRecord has health metrics, calendar events, and messaging
    summaries for that day, all in one place.
    """
    try:
        records = await mcp_client.fetch_day_records(
            user_id=user_id,
            start=start.isoformat(),
            end=end.isoformat(),
        )
        return records
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"MCP fetch failed: {e}")


@router.get("/insights", response_model=InsightResponse)
async def get_insights(
    user_id: str = Query(...),
    days: int = Query(default=30, ge=7, le=90, description="How many days to analyze"),
    mcp_client=Depends(get_mcp_client),
):
    """
    The main endpoint. Fetches data, runs pattern detection, returns insights.

    Flow:
      1. Fetch DayRecords from all 3 MCP servers (via MCPClient)
      2. Send to ML engine for pattern detection        
      3. Run RAG to find similar historical weeks       
      4. Return InsightResponse with insights + timeline

    For now returns a stub response so the frontend can develop against it.
    """
    end = date.today()
    start = end - timedelta(days=days)

    try:
        timeline = await mcp_client.fetch_day_records(
            user_id=user_id,
            start=start.isoformat(),
            end=end.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"MCP fetch failed: {e}")

    # TODO: pass timeline to ml-engine for real pattern detection
    # For now, return the raw data so the frontend isn't blocked.
    from datetime import datetime
    return InsightResponse(
        user_id=user_id,
        generated_at=datetime.utcnow(),
        summary="Pattern analysis coming soon. Data pipeline is connected.",
        insights=[],
        timeline=timeline,
    )
