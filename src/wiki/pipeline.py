"""Open Wiki pipeline — compile raw docs into pages, then query the wiki."""

from __future__ import annotations

import re
from pathlib import Path

from src.config import settings
from src.llm.provider import Message, llm
from src.wiki.store import WikiPage, wiki_store

COMPILE_SYSTEM_PROMPT = """You are a wiki page compiler. Given one raw source document, create
a structured markdown wiki page. The page should:
- Start with a clear summary (2-3 sentences)
- Use headings and bullet points
- Include [[wikilinks]] to related concepts when relevant
- Note key facts the reader should remember
- Be concise but complete

Output ONLY the markdown body (no frontmatter). Use this structure:
## Summary
...
## Key Points
...
## Related
- [[concepts/other-topic]]
"""

WIKI_QUERY_SYSTEM_PROMPT = """You are a helpful assistant that answers questions using the wiki pages below.
The wiki is a persistent, compiled knowledge base — not raw document chunks.
Use ONLY the wiki content to answer. Cite which wiki page(s) your answer comes from.
If the answer is not in the wiki, say "I don't have that information in the wiki yet."

Wiki pages:
{context}
"""


def _slugify(name: str) -> str:
    base = Path(name).stem.lower()
    # Sample files use ordering prefixes such as "01_". They are useful in the
    # source folder but should not create duplicate topic pages in the wiki.
    base = re.sub(r"^\d+[\s_-]*", "", base)
    base = re.sub(r"[^a-z0-9]+", "-", base)
    return base.strip("-")


def _demo_compile_page(source_name: str, text: str) -> tuple[str, str, str]:
    """Build a deterministic, source-faithful page without claiming LLM synthesis."""
    topic = _slugify(source_name)
    title = topic.replace("-", " ").title()
    slug = f"concepts/{_slugify(source_name)}"

    lines = text.strip().splitlines()
    markdown_lines: list[str] = []
    skip_next = False
    for index, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
        next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""
        if next_line and set(next_line) <= {"="}:
            markdown_lines.append(f"# {line.strip()}")
            skip_next = True
        elif next_line and set(next_line) <= {"-"}:
            markdown_lines.append(f"## {line.strip()}")
            skip_next = True
        else:
            markdown_lines.append(line)

    body_parts = [
        "## Summary",
        (
            f"Demo mode converted `{source_name}` into a persistent wiki page "
            "without using an LLM. The source content is preserved below rather "
            "than being presented as AI-generated synthesis."
        ),
        "",
        "## Source Knowledge",
        "",
        *markdown_lines,
        "",
        "## Related",
        "- [[index]]",
    ]
    return slug, title, "\n".join(body_parts)


def compile_file(file_path: Path) -> str:
    """Compile one raw document into a wiki page."""
    text = file_path.read_text(encoding="utf-8")
    slug = f"concepts/{_slugify(file_path.name)}"
    title = _slugify(file_path.name).replace("-", " ").title()

    if llm.is_demo_mode:
        slug, title, body = _demo_compile_page(file_path.name, text)
        wiki_store.write_page(slug, title, body, source=file_path.name, tags=["compiled"])
        return slug

    messages = [
        Message(role="system", content=COMPILE_SYSTEM_PROMPT),
        Message(
            role="user",
            content=f"Source file: {file_path.name}\n\n{text[:6000]}",
        ),
    ]
    response = llm.chat(messages, temperature=0.3)
    wiki_store.write_page(slug, title, response.content, source=file_path.name, tags=["compiled"])
    return slug


def compile_directory(directory: Path) -> dict[str, str]:
    """Compile all .txt and .md files from a directory into wiki pages."""
    results: dict[str, str] = {}
    for pattern in ("*.txt", "*.md"):
        for file_path in sorted(directory.glob(pattern)):
            slug = compile_file(file_path)
            results[file_path.name] = slug

    _ensure_index()
    return results


def _ensure_index() -> None:
    """Create or refresh the wiki index page."""
    from src.wiki.store import list_pages

    slugs = [s for s in list_pages() if s != "index"]
    lines = [
        "# AI Learning Lab Wiki",
        "",
        "A persistent markdown knowledge base. Unlike RAG, queries read topic pages",
        "instead of retrieving raw vector chunks. Re-run compilation when source files change.",
        "",
        "## Pages",
    ]
    for slug in sorted(slugs):
        page = wiki_store.get_page(slug)
        if page:
            lines.append(f"- [[{slug}|{page.title}]]")

    lines.extend(
        [
            "",
            "## RAG vs Open Wiki",
            "",
            "| | RAG | Open Wiki |",
            "|---|-----|-----------|",
            "| Storage | Vector chunks | Markdown pages |",
            "| Retrieval | Embedding similarity | Page search + read |",
            "| Knowledge | Raw chunks selected each query | Persistent pages rebuilt on compile |",
            "| Best for | Semantic passage retrieval | Browsable, curated topic pages |",
        ]
    )
    wiki_store.write_page("index", "Wiki Index", "\n".join(lines), tags=["index"])


def wiki_search(query: str, top_k: int = 3) -> list[tuple[WikiPage, float]]:
    """Search the wiki for relevant pages."""
    return wiki_store.search(query, top_k=top_k)


def wiki_query(question: str, top_k: int = 3) -> dict:
    """
    Open Wiki query pipeline: Search pages → Read compiled knowledge → Generate answer.

    Contrast with RAG:
    - RAG: embed query → find similar chunks → generate
    - Wiki: find relevant pages → read synthesized content → generate
    """
    matches = wiki_search(question, top_k=top_k)

    if not matches:
        return {
            "answer": (
                "No wiki pages found. Click 'Compile Sample Docs' in the Open Wiki tab "
                "or run: python scripts/compile_wiki.py"
            ),
            "pages": [],
            "approach": "open_wiki",
        }

    context_parts = []
    pages_out = []
    for i, (page, score) in enumerate(matches, 1):
        context_parts.append(f"### [{i}] {page.title} (wiki/{page.slug})\n{page.content}")
        pages_out.append(
            {
                "slug": page.slug,
                "title": page.title,
                "score": round(score, 2),
                "source": page.source,
                "preview": page.content[:300] + ("..." if len(page.content) > 300 else ""),
            }
        )

    context = "\n\n".join(context_parts)
    messages = [
        Message(role="system", content=WIKI_QUERY_SYSTEM_PROMPT.format(context=context)),
        Message(role="user", content=question),
    ]

    response = llm.chat(messages, temperature=0.3)
    answer = response.content

    if llm.is_demo_mode:
        answer = (
            "[Demo Mode — showing matched wiki pages]\n\n"
            + "\n\n---\n\n".join(
                f"**Wiki page: {p['title']}** (`{p['slug']}`, relevance: {p['score']})\n{p['preview']}"
                for p in pages_out
            )
            + "\n\n_Set LLM_PROVIDER=ollama or openai for generated answers._"
        )

    return {
        "answer": answer,
        "pages": pages_out,
        "approach": "open_wiki",
    }


def compile_sample_docs() -> dict[str, str]:
    """Compile the project's sample learning documents into the wiki."""
    raw_dir = Path(settings.sample_docs_dir)
    return compile_directory(raw_dir)
