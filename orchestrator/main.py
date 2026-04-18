"""
Orchestrator — entry point.

This is the FastAPI application. It does three things:
  1. On startup: connects to all 3 MCP servers and holds those connections open.
  2. While running: serves REST endpoints the frontend calls (via api/routes.py).
  3. On shutdown: gracefully closes all MCP connections.

The startup/shutdown logic uses FastAPI's `lifespan` pattern — a single async
generator that yields once. Code before the yield runs on startup; code after
runs on shutdown. 

Run locally (outside Docker):
    uvicorn main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mcp_client.client import MCPClient
from api.routes import router
from auth.routes import router as auth_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# Lifespan 
# This runs once when the server starts and once when it stops.
# We attach the MCPClient to app.state so route handlers can access it
# via dependency injection (see api/routes.py → get_mcp_client).

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    logger.info("Orchestrator starting up...")

    mcp_client = MCPClient()
    try:
        await mcp_client.connect()
    except Exception as e:
        # Log without crashing to allow the orchestrator to start in partial mode for now
        logger.warning(f"MCP connection failed at startup: {e}")

    app.state.mcp_client = mcp_client

    yield  # <-- server is live here, handling requests

    # --- SHUTDOWN ---
    logger.info("Orchestrator shutting down...")
    await mcp_client.disconnect()


# App
app = FastAPI(
    title="ContextMirror Orchestrator",
    description="MCP client + pattern engine API for the ContextMirror app.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS to allow the React Native frontend to call this API
# In production, need to lock down allow_origins to specific URLs.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)   # POST /auth/register, POST /auth/login
app.include_router(router)        # GET /api/v1/timeline, GET /api/v1/insights
