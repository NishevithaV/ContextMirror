"""
REST API routes — what the frontenda calls.
"""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.requests import Request

from mcp_client.models import DayRecord, InsightResponse
from auth.deps import get_current_user
from rag.pipeline import RAGPipeline

router = APIRouter(prefix="/api/v1")


# Dependency: get the MCP client from app state 
# FastAPI's dependency injection system allows to declare shared
# resources that routes need. 

def get_mcp_client(request: Request):
    return request.app.state.mcp_client


def get_rag(request: Request) -> RAGPipeline:
    return request.app.state.rag


# Routes 
@router.get("/health")
async def health_check():
    """Simple liveness check. Load balancers and Docker healthchecks call this."""
    return {"status": "ok"}


@router.get("/timeline", response_model=list[DayRecord])
async def get_timeline(
    start: date = Query(
        default_factory=lambda: date.today() - timedelta(days=30),
        description="Start date (default: 30 days ago)",
    ),
    end: date = Query(
        default_factory=date.today,
        description="End date (default: today)",
    ),
    current_user: dict = Depends(get_current_user),
    mcp_client=Depends(get_mcp_client),
):
    """
    Fetch the raw unified timeline — one DayRecord per day.
    Requires a valid JWT in the Authorization header.
    user_id is taken from the token, not the query string.
    """
    try:
        records = await mcp_client.fetch_day_records(
            user_id=current_user["id"],
            start=start.isoformat(),
            end=end.isoformat(),
        )
        return records
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"MCP fetch failed: {e}")


@router.get("/insights", response_model=InsightResponse)
async def get_insights(
    days: int = Query(default=30, ge=7, le=90, description="How many days to analyze"),
    current_user: dict = Depends(get_current_user),
    mcp_client=Depends(get_mcp_client),
    rag: RAGPipeline = Depends(get_rag),
):
    """
    The main endpoint. Fetches data, runs RAG retrieval, returns insights.

    Flow:
      1. Fetch DayRecords from all 3 MCP servers (via MCPClient)
      2. Store this week in ChromaDB (upsert)
      3. Retrieve similar historical weeks via cosine similarity
      4. TODO: pass timeline + similar_weeks to ML engine
      5. Return InsightResponse
    """
    end = date.today()
    start = end - timedelta(days=days)

    try:
        timeline = await mcp_client.fetch_day_records(
            user_id=current_user["id"],
            start=start.isoformat(),
            end=end.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"MCP fetch failed: {e}")

    # Store this week and find similar past weeks
    try:
        rag.store_week(current_user["id"], timeline)
        similar_weeks = rag.find_similar_weeks(current_user["id"], timeline)
    except Exception as e:
        # RAG failure is non-fatal, insights still work without historical context
        similar_weeks = []

    # TODO: pass timeline + similar_weeks to ml-engine for real pattern detection
    from datetime import datetime, timezone
    summary = "Pattern analysis coming soon."
    if similar_weeks:
        top = similar_weeks[0]
        summary = (
            f"This week is most similar to {top['week']} "
            f"(similarity: {top['similarity']:.0%}). "
            "Full pattern analysis coming soon."
        )

    return InsightResponse(
        user_id=current_user["id"],
        generated_at=datetime.now(timezone.utc),
        summary=summary,
        insights=[],
        timeline=timeline,
    )
