"""MCP server for Medical Assistant tools."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcp.server import MCPServer

from medical_assistant.src.agents.tools import (
    TOOLS,
    bmi_calculator,
    find_specialist,
    medication_info,
    symptom_lookup,
)
from medical_assistant.src.rag.pipeline import medical_rag_query

server = MCPServer("medical-assistant-lab")


@server.tool()
def calc_bmi(weight_kg: float, height_m: float) -> str:
    """Calculate BMI (educational only)."""
    return bmi_calculator(weight_kg, height_m)


@server.tool()
def symptoms(symptom: str) -> str:
    """Look up educational symptom information."""
    return symptom_lookup(symptom)


@server.tool()
def medication(drug_name: str) -> str:
    """Look up educational medication information."""
    return medication_info(drug_name)


@server.tool()
def specialist(specialty: str, city: str = "your area") -> str:
    """Find mock specialist listings."""
    return find_specialist(specialty, city)


@server.tool()
def medical_search(query: str) -> str:
    """Search medical education knowledge base via RAG."""
    result = medical_rag_query(query)
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    server.run(transport="stdio")
