"""
MCP (Model Context Protocol) Server.

Concept: MCP
- A standard protocol for AI models to connect to external tools and data
- Like USB for AI: one protocol, many compatible tools/servers
- Cursor, Claude Desktop, and other AI apps use MCP to extend capabilities

This server exposes our learning lab tools via MCP so any MCP-compatible
client can use them.

Run: python -m src.mcp.server
"""

from __future__ import annotations

import json

from mcp.server import MCPServer

from src.agents.tools import calculator, get_current_time, get_weather
from src.rag.pipeline import rag_query
from src.wiki.pipeline import wiki_query

server = MCPServer("ai-learning-lab")


@server.tool()
def calc(expression: str) -> str:
    """Evaluate a math expression like '2 + 2' or 'sqrt(16)'."""
    return calculator(expression)


@server.tool()
def weather(city: str) -> str:
    """Get deterministic mock weather for a city; this is not live data."""
    return get_weather(city)


@server.tool()
def current_time() -> str:
    """Get the current date and time."""
    return get_current_time()


@server.tool()
def rag_search(query: str) -> str:
    """Search the knowledge base using RAG and return the answer."""
    result = rag_query(query)
    return json.dumps(result, indent=2)


@server.tool()
def wiki_search(query: str) -> str:
    """Search the Open Wiki — compiled markdown knowledge pages."""
    result = wiki_query(query)
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    server.run(transport="stdio")
