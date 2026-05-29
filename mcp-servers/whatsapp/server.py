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

mcp = FastMCP("whatsapp-mcp")

register_message_tools(mcp)
register_analytics_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=PORT)
