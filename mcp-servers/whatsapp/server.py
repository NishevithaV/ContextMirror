"""
WhatsApp MCP Server — entry point.

This creates a FastMCP server instance, registers all tools onto it,
and starts serving over SSE so the orchestrator can connect.

FastMCP vs the low-level MCP Server class:
  - Low-level: you manually call server.setRequestHandler() for every
    protocol message type (list_tools, call_tool, list_resources, etc.)
  - FastMCP: you write @mcp.tool() decorated functions and it handles
    all the protocol wiring for you.
  FastMCP is the right choice here — we want to focus on the tools,
  not the protocol plumbing.

Transport — SSE:
  We use SSE (not stdio) because this server runs in Docker and the
  orchestrator connects to it over the network. stdio transport is for
  local subprocess connections (e.g. Claude Desktop spinning up a server
  as a child process). SSE is for service-to-service communication.

Run locally (outside Docker):
    WHATSAPP_DB_PATH=./path/to/whatsapp.db uvicorn server:app --port 3002
"""

import os
import logging
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from tools import register_message_tools, register_analytics_tools

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

PORT = int(os.getenv("PORT", "3002"))

# Create the FastMCP instance. The name is what shows up in MCP logs
# and in the orchestrator's startup output when it calls list_tools().
mcp = FastMCP("whatsapp-mcp")

# Register all tools. Splitting into message tools and analytics tools
# is just organization — to the MCP protocol they're all the same.
register_message_tools(mcp)
register_analytics_tools(mcp)

# FastMCP exposes a .sse_app() method that returns a standard ASGI app
# you can run with uvicorn. This gives us the /sse and /messages endpoints
# the orchestrator's SSE client connects to.
app = mcp.sse_app()
