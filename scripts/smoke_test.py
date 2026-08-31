"""Quick smoke test for the AI Learning Lab."""

from __future__ import annotations

import asyncio
import compileall
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

errors: list[str] = []


def check(name: str, fn) -> None:
    try:
        fn()
        print(f"OK  {name}")
    except Exception as exc:
        errors.append(f"{name}: {exc}")
        print(f"FAIL {name}: {exc}")


def test_imports() -> None:
    for module in [
        "src.config",
        "src.llm.provider",
        "src.chat.service",
        "src.rag.pipeline",
        "src.rag.vectorstore",
        "src.wiki.store",
        "src.wiki.pipeline",
        "src.agents.tools",
        "src.agents.agent",
        "src.mcp.server",
    ]:
        __import__(module)


def test_wiki() -> None:
    from src.wiki.pipeline import wiki_query
    from src.wiki.store import list_pages, wiki_store

    assert wiki_store.page_count > 0
    assert list_pages()
    result = wiki_query("What is Open Wiki vs RAG?")
    assert result["answer"]
    assert result["pages"]


def test_demo_wiki_compilation() -> None:
    from src.config import settings
    from src.llm.provider import llm
    from src.wiki.pipeline import compile_directory

    if not llm.is_demo_mode:
        return

    original_pages_dir = settings.wiki_pages_dir
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_dir = root / "sources"
            source_dir.mkdir()
            (source_dir / "01_topic_name.txt").write_text(
                "Topic Name\n==========\n\nA source-faithful fact.",
                encoding="utf-8",
            )
            settings.wiki_pages_dir = str(root / "wiki")
            result = compile_directory(source_dir)
            assert result == {"01_topic_name.txt": "concepts/topic-name"}
            page_path = root / "wiki" / "concepts" / "topic-name.md"
            content = page_path.read_text(encoding="utf-8")
            assert "A source-faithful fact." in content
            assert not (root / "wiki" / "concepts" / "01-topic-name.md").exists()
    finally:
        settings.wiki_pages_dir = original_pages_dir


def test_rag() -> None:
    from src.rag.pipeline import rag_query

    result = rag_query("What is RAG?")
    assert "answer" in result


def test_agent_tools() -> None:
    from src.agents.tools import TOOLS, execute_tool

    expected = {
        "calculator",
        "get_weather",
        "get_current_time",
        "search_knowledge",
        "search_wiki",
    }
    assert expected.issubset(TOOLS.keys())
    assert execute_tool("calculator", {"expression": "2 + 2"}) == "4"
    assert execute_tool("search_wiki", {"query": "Open Wiki"})


def test_mcp_registration() -> None:
    from src.mcp.server import server

    tools = asyncio.run(server.list_tools())
    names = {tool.name for tool in tools}
    assert names == {"calc", "weather", "current_time", "rag_search", "wiki_search"}


def test_demo_agent_routing() -> None:
    from src.agents.agent import Agent
    from src.llm.provider import llm

    if not llm.is_demo_mode:
        return

    result = Agent().run("Search the wiki: what is Open Wiki?")
    assert result.steps
    assert result.steps[0].tool_name == "search_wiki"
    assert result.steps[0].tool_output


def test_demo_chat_memory() -> None:
    from src.chat.service import ChatSession
    from src.llm.provider import llm

    if not llm.is_demo_mode:
        return

    session = ChatSession()
    session.send("My name is Alex")
    reply = session.send("What is my name?")
    assert "Alex" in reply


def test_demo_multi_tool_agent() -> None:
    from src.agents.agent import Agent
    from src.llm.provider import llm

    if not llm.is_demo_mode:
        return

    result = Agent().run("What's 15*23 and the weather in Tokyo?")
    tool_names = [step.tool_name for step in result.steps if step.tool_name]
    assert tool_names == ["calculator", "get_weather"], tool_names
    assert "345" in result.answer
    assert "Tokyo" in result.answer


def test_app_syntax() -> None:
    assert compileall.compile_file(str(ROOT / "app.py"), quiet=1)


def main() -> int:
    check("imports", test_imports)
    check("wiki", test_wiki)
    check("demo wiki compilation", test_demo_wiki_compilation)
    check("rag", test_rag)
    check("agent tools", test_agent_tools)
    check("MCP registration", test_mcp_registration)
    check("demo agent routing", test_demo_agent_routing)
    check("demo chat memory", test_demo_chat_memory)
    check("demo multi-tool agent", test_demo_multi_tool_agent)
    check("app.py syntax", test_app_syntax)

    if errors:
        print("\nFailed checks:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
