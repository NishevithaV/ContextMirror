# ContextMirror

Users connect their personal data sources via MCP servers, and an agentic orchestrator pulls context through those standardized protocols to spot behavioral patterns, summarize trends, and ask neutral reflective questions, surfacing correlations no single app can produce.

## Architecture Overview

```
frontend/          React + Vite (web)          
mcp-servers/
  calendar/        Google Calendar MCP Server  
  whatsapp/        WhatsApp MCP Server         
  health/          Health/Fitness MCP Server   
orchestrator/      MCP Client + FastAPI + RAG   
ml-engine/         Pattern Engine + Fine-tuning 
shared/
  schema.json      THE shared data contract    
  training-data/   LLM fine-tuning examples    
```

## The Data Contract

**`shared/schema.json` is the single source of truth.** All MCP servers return data in the shapes defined there. The orchestrator assembles `DayRecord` objects from all three servers and the frontend renders `InsightResponse` objects. 

Key types:
- `DayRecord` - unified snapshot of one day (health + calendar + messaging)
- `PatternInsight` - a pattern detected by the ML engine (correlation, trend, anomaly, cluster)
- `InsightResponse` - what the orchestrator returns to the frontend

## How It Works

1. On each request, the orchestrator calls all three MCP servers in parallel
2. Data is merged into a `DayRecord` per day, a unified snapshot of health, calendar, and messaging
3. The RAG pipeline stores weekly summaries as embeddings in ChromaDB and retrieves similar past weeks
4. The ML engine (locally fine-tuned Phi-3/Mistral) detects patterns and returns insights
5. The frontend renders the timeline and surfaced correlations

## Running Locally

```bash
# Start all backend services (requires Docker)
docker-compose up --build

# Start the frontend (separate terminal)
cd frontend && npm install && npm start
```

Copy `.env.example` to `.env` and fill in your credentials before running.

## MCP Protocol Basics

Each data source runs as an independent **MCP server** that exposes **tools** — structured functions the orchestrator can call via JSON-RPC 2.0 over SSE (HTTP). The orchestrator is an **MCP client** that connects to all three servers and coordinates data flow.

MCP references:
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- Protocol spec: https://modelcontextprotocol.io

## Environment Variables

| Variable               | Used by      | Description                        |
|------------------------|-------------|-------------------------------------|
| `GOOGLE_CLIENT_ID`     | calendar-mcp | Google OAuth client ID             |
| `GOOGLE_CLIENT_SECRET` | calendar-mcp | Google OAuth client secret         |
| `JWT_SECRET_KEY`       | orchestrator | Secret for signing JWT tokens      |