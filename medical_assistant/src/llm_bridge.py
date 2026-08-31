"""Bridge to shared LLM provider from main project."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.llm.provider import LLMProvider, Message, llm  # noqa: E402

__all__ = ["LLMProvider", "Message", "llm"]
