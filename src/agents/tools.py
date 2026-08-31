"""Agent tools — functions the AI agent can call."""

from __future__ import annotations

import ast
import math
import operator
from datetime import datetime
from typing import Any, Callable


_BINARY_OPERATORS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_MATH_NAMES = {
    name: value
    for name, value in vars(math).items()
    if not name.startswith("_") and (callable(value) or isinstance(value, (int, float)))
}
_MATH_NAMES.update({"abs": abs, "round": round, "min": min, "max": max})


def _evaluate_math(node: ast.AST) -> float | int:
    if isinstance(node, ast.Expression):
        return _evaluate_math(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate_math(node.left)
        right = _evaluate_math(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Exponent is too large")
        return _BINARY_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate_math(node.operand))
    if isinstance(node, ast.Name) and node.id in _MATH_NAMES:
        value = _MATH_NAMES[node.id]
        if isinstance(value, (int, float)):
            return value
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        function = _MATH_NAMES.get(node.func.id)
        if callable(function) and not node.keywords:
            return function(*[_evaluate_math(argument) for argument in node.args])
    raise ValueError("Only numbers, arithmetic operators, and named math functions are allowed")


def calculator(expression: str) -> str:
    """Safely evaluate a math expression."""
    try:
        if len(expression) > 200:
            raise ValueError("Expression is too long")
        parsed = ast.parse(expression, mode="eval")
        return str(_evaluate_math(parsed))
    except (SyntaxError, TypeError, ValueError, ZeroDivisionError, OverflowError) as exc:
        return f"Error: {exc}"


def get_weather(city: str) -> str:
    """Mock weather lookup (in production, call a real weather API)."""
    mock_data = {
        "london": {"temp": 15, "condition": "Cloudy"},
        "new york": {"temp": 22, "condition": "Sunny"},
        "tokyo": {"temp": 28, "condition": "Humid"},
        "paris": {"temp": 18, "condition": "Rainy"},
    }
    data = mock_data.get(city.lower(), {"temp": 20, "condition": "Clear"})
    return f"Weather in {city}: {data['temp']}°C, {data['condition']}"


def get_current_time() -> str:
    """Return the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def search_knowledge(query: str) -> str:
    """Search the RAG knowledge base."""
    from src.rag.pipeline import rag_query

    result = rag_query(query, top_k=2)
    if not result["chunks"]:
        return "No relevant documents found."
    return result["answer"]


def search_wiki(query: str) -> str:
    """Search the Open Wiki knowledge base."""
    from src.wiki.pipeline import wiki_query

    result = wiki_query(query, top_k=2)
    if not result["pages"]:
        return "No relevant wiki pages found."
    return result["answer"]


# Registry of all available tools
TOOLS: dict[str, Callable[..., str]] = {
    "calculator": calculator,
    "get_weather": get_weather,
    "get_current_time": get_current_time,
    "search_knowledge": search_knowledge,
    "search_wiki": search_wiki,
}


# OpenAI function-calling schema for each tool
TOOL_SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a mathematical expression. Supports +, -, *, /, sqrt, sin, cos, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The math expression to evaluate, e.g. '2 + 2' or 'sqrt(16)'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get deterministic mock weather for a city (not live data).",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name, e.g. 'London'"}
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "Search the RAG document knowledge base for information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_wiki",
            "description": "Search the Open Wiki — compiled markdown knowledge pages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"],
            },
        },
    },
]


def execute_tool(name: str, arguments: dict[str, Any]) -> str:
    """Run a tool by name with the given arguments."""
    if name not in TOOLS:
        return f"Unknown tool: {name}"
    try:
        return TOOLS[name](**arguments)
    except (TypeError, ValueError) as exc:
        return f"Invalid arguments for {name}: {exc}"
