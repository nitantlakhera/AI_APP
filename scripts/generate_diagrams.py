"""Generate PNG architecture diagrams for documentation."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "docs" / "images"

# Colors (readable on white background)
BLUE = "#2563eb"
GREEN = "#059669"
PURPLE = "#7c3aed"
PINK = "#db2777"
ORANGE = "#d97706"
GRAY = "#64748b"
DARK = "#1e293b"
LIGHT_BLUE = "#dbeafe"
LIGHT_GREEN = "#d1fae5"
LIGHT_PURPLE = "#ede9fe"
LIGHT_ORANGE = "#ffedd5"
LIGHT_GRAY = "#f1f5f9"


def _box(ax, x, y, w, h, text, facecolor, edgecolor=DARK, fontsize=9, bold=False):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.5,
        edgecolor=edgecolor,
        facecolor=facecolor,
    )
    ax.add_patch(patch)
    weight = "bold" if bold else "normal"
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=DARK,
        weight=weight,
        wrap=True,
    )
    return patch


def _arrow(ax, x1, y1, x2, y2, color=GRAY):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.5,
            color=color,
            shrinkA=2,
            shrinkB=2,
        )
    )


def _save(fig, name: str) -> str:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(path)


def draw_llm_architecture() -> str:
    """How Chat, RAG, and Agent connect to the shared LLM provider."""
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("LLM Architecture — Shared Brain for All Features", fontsize=14, weight="bold", pad=16)

    # UI layer
    _box(ax, 4.2, 6.0, 3.6, 0.7, "Streamlit UI (app.py)", LIGHT_GRAY, bold=True)

    # Feature tabs
    _box(ax, 0.4, 4.6, 2.2, 0.8, "Chat Tab\nchat/service.py", LIGHT_BLUE)
    _box(ax, 3.4, 4.6, 2.2, 0.8, "RAG Tab\nrag/pipeline.py", LIGHT_GREEN)
    _box(ax, 6.4, 4.6, 2.2, 0.8, "Agent Tab\nagents/agent.py", LIGHT_PURPLE)
    _box(ax, 9.4, 4.6, 2.2, 0.8, "Fine-Tune Tab\nfine_tuning/", LIGHT_ORANGE)

    # Shared LLM
    _box(ax, 3.0, 2.8, 6.0, 1.0, "LLM Provider (src/llm/provider.py)\nSingle gateway: chat(), tools, demo fallback", "#bfdbfe", BLUE, 10, True)

    # Backends
    _box(ax, 0.8, 0.8, 2.8, 0.9, "Demo Mode\n(no API key)", LIGHT_GRAY)
    _box(ax, 4.6, 0.8, 2.8, 0.9, "Ollama\n(local LLM)", LIGHT_BLUE)
    _box(ax, 8.4, 0.8, 2.8, 0.9, "OpenAI\n(cloud API)", LIGHT_GREEN)

    # Data for RAG/Agent
    _box(ax, 0.4, 2.8, 2.2, 1.0, "ChromaDB\n+ Embeddings", LIGHT_GREEN)
    _box(ax, 9.4, 2.8, 2.2, 1.0, "Agent Tools\ncalculator, weather,\nsearch_knowledge", LIGHT_PURPLE)

    # Arrows UI -> features
    for x in (1.5, 4.5, 7.5, 10.5):
        _arrow(ax, 6.0, 6.0, x, 5.4)

    # Features -> LLM
    _arrow(ax, 1.5, 4.6, 4.5, 3.8, BLUE)
    _arrow(ax, 4.5, 4.6, 5.5, 3.8, GREEN)
    _arrow(ax, 7.5, 4.6, 6.5, 3.8, PURPLE)
    _arrow(ax, 10.5, 4.6, 8.0, 3.8, ORANGE)

    # LLM -> backends
    _arrow(ax, 4.5, 2.8, 2.2, 1.7)
    _arrow(ax, 6.0, 2.8, 6.0, 1.7)
    _arrow(ax, 7.5, 2.8, 9.8, 1.7)

    # RAG/Agent data
    _arrow(ax, 1.5, 3.8, 2.6, 4.6, GREEN)
    _arrow(ax, 10.5, 3.8, 9.0, 4.6, PURPLE)
    _arrow(ax, 2.6, 3.3, 4.5, 3.3, GREEN)
    _arrow(ax, 9.0, 3.3, 7.5, 3.3, PURPLE)

    ax.text(6.0, 0.2, "Set LLM_PROVIDER in .env → demo | ollama | openai", ha="center", fontsize=9, color=GRAY)
    return _save(fig, "llm-architecture.png")


def draw_pipeline_structure() -> str:
    """RAG and Agent pipelines step by step."""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_title("Pipeline Structure — How Data Flows Through the App", fontsize=14, weight="bold", pad=16)

    # Chat pipeline
    ax.text(0.4, 7.5, "1. Chat Pipeline", fontsize=11, weight="bold", color=BLUE)
    steps_chat = ["User\nmessage", "Add to\nhistory", "LLM\nchat()", "Assistant\nreply"]
    for i, label in enumerate(steps_chat):
        _box(ax, 0.4 + i * 2.7, 6.5, 2.2, 0.8, label, LIGHT_BLUE)
        if i < len(steps_chat) - 1:
            _arrow(ax, 0.4 + i * 2.7 + 2.2, 6.9, 0.4 + (i + 1) * 2.7, 6.9, BLUE)

    # RAG pipeline
    ax.text(0.4, 5.6, "2. RAG Pipeline (Retrieve → Augment → Generate)", fontsize=11, weight="bold", color=GREEN)
    steps_rag = [
        "Question",
        "Embed\nquery",
        "Search\nChromaDB",
        "Top-K\nchunks",
        "Build\nprompt",
        "LLM\ngenerate",
        "Answer +\nsources",
    ]
    for i, label in enumerate(steps_rag):
        _box(ax, 0.3 + i * 1.65, 4.5, 1.45, 0.85, label, LIGHT_GREEN, fontsize=8)
        if i < len(steps_rag) - 1:
            _arrow(ax, 0.3 + i * 1.65 + 1.45, 4.92, 0.3 + (i + 1) * 1.65, 4.92, GREEN)

    # Agent pipeline
    ax.text(0.4, 3.5, "3. Agent Pipeline (ReAct: Reason + Act loop)", fontsize=11, weight="bold", color=PURPLE)
    steps_agent = [
        "User\ntask",
        "LLM\nthinks",
        "Need\ntool?",
        "Call\ntool",
        "Tool\nresult",
        "Final\nanswer",
    ]
    for i, label in enumerate(steps_agent):
        _box(ax, 0.4 + i * 1.9, 2.4, 1.6, 0.85, label, LIGHT_PURPLE, fontsize=8)
        if i < len(steps_agent) - 1:
            _arrow(ax, 0.4 + i * 1.9 + 1.6, 2.82, 0.4 + (i + 1) * 1.9, 2.82, PURPLE)

    # Loop back arrow for agent
    ax.annotate(
        "loop until done (max 5 steps)",
        xy=(3.2, 2.4),
        xytext=(7.5, 1.5),
        fontsize=8,
        color=PURPLE,
        arrowprops=dict(arrowstyle="-|>", color=PURPLE, lw=1.2),
    )

    # Fine-tuning pipeline
    ax.text(0.4, 1.3, "4. Fine-Tuning Pipeline (LoRA)", fontsize=11, weight="bold", color=ORANGE)
    steps_ft = ["JSONL\ndataset", "Tokenize\n+ format", "Train\nLoRA", "Adapter\nsaved", "Infer /\nEvaluate"]
    for i, label in enumerate(steps_ft):
        _box(ax, 0.4 + i * 2.3, 0.3, 2.0, 0.8, label, LIGHT_ORANGE, fontsize=8)
        if i < len(steps_ft) - 1:
            _arrow(ax, 0.4 + i * 2.3 + 2.0, 0.7, 0.4 + (i + 1) * 2.3, 0.7, ORANGE)

    return _save(fig, "pipeline-structure.png")


def draw_integration_overview() -> str:
    """High-level system map."""
    fig, ax = plt.subplots(figsize=(12, 7.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis("off")
    ax.set_title("System Integration Overview", fontsize=14, weight="bold", pad=16)

    # Main app box
    main = FancyBboxPatch(
        (0.5, 3.2),
        7.0,
        3.8,
        boxstyle="round,pad=0.03,rounding_size=0.1",
        linewidth=2,
        edgecolor=BLUE,
        facecolor="#f8fafc",
        linestyle="-",
    )
    ax.add_patch(main)
    ax.text(4.0, 6.7, "Main App — Integrated Product (app.py)", ha="center", fontsize=11, weight="bold", color=BLUE)

    _box(ax, 1.0, 5.5, 1.5, 0.7, "Chat", LIGHT_BLUE, BLUE, 9, True)
    _box(ax, 2.8, 5.5, 1.5, 0.7, "RAG", LIGHT_GREEN, GREEN, 9, True)
    _box(ax, 4.6, 5.5, 1.5, 0.7, "Agent", LIGHT_PURPLE, PURPLE, 9, True)
    _box(ax, 6.4, 5.5, 1.5, 0.7, "Fine-Tune", LIGHT_ORANGE, ORANGE, 9, True)

    _box(ax, 2.0, 4.0, 4.0, 0.9, "Shared LLM Provider", "#bfdbfe", BLUE, 10, True)
    _box(ax, 1.0, 3.4, 2.5, 0.8, "ChromaDB\nsample_docs/", LIGHT_GREEN, GREEN, 8)
    _box(ax, 4.5, 3.4, 2.5, 0.8, "Agent Tools\n+ RAG search", LIGHT_PURPLE, PURPLE, 8)

    # MCP
    _box(ax, 8.2, 5.0, 3.2, 1.2, "MCP Server\nsrc/mcp/server.py\n(separate process)", LIGHT_GRAY, GRAY, 9, True)
    _box(ax, 8.2, 3.2, 3.2, 1.2, "Medical Assistant\nmedical_assistant/app.py\n(domain app)", "#fce7f3", PINK, 9, True)

    # External
    _box(ax, 8.2, 1.2, 3.2, 0.9, "Cursor / Claude Desktop", LIGHT_GRAY, GRAY, 9)

    _arrow(ax, 7.5, 5.6, 8.2, 5.6, GRAY)
    _arrow(ax, 9.8, 5.0, 9.8, 2.1, GRAY)
    ax.text(10.5, 4.0, "stdio\nMCP", fontsize=8, color=GRAY)

    ax.text(4.0, 2.5, "Agent search_knowledge → same RAG pipeline as RAG tab", ha="center", fontsize=8, color=GREEN)
    ax.text(4.0, 2.0, "All features share one LLM — switch provider in .env", ha="center", fontsize=8, color=GRAY)

    return _save(fig, "integration-overview.png")


def main() -> None:
    paths = [
        draw_llm_architecture(),
        draw_pipeline_structure(),
        draw_integration_overview(),
    ]
    print("Generated diagrams:")
    for path in paths:
        print(f"  - {path}")


if __name__ == "__main__":
    main()
