"""Wiki filesystem — read, search, and write markdown wiki pages."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from src.config import settings

_SEARCH_STOP_WORDS = {
    "and",
    "are",
    "does",
    "for",
    "from",
    "how",
    "that",
    "the",
    "this",
    "what",
    "when",
    "where",
    "which",
    "with",
}


@dataclass
class WikiPage:
    """A single wiki page with parsed metadata."""

    slug: str
    title: str
    content: str
    raw_text: str
    source: str | None = None
    tags: list[str] | None = None


def _pages_dir() -> Path:
    return Path(settings.wiki_pages_dir)


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse optional YAML-like frontmatter from markdown."""
    if not text.startswith("---"):
        return {}, text

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}, text

    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip().strip('"').strip("'")

    body = text[match.end() :]
    return meta, body


def _slug_to_path(slug: str) -> Path:
    parts = [part for part in slug.replace("\\", "/").split("/") if part]
    if not parts or any(
        part in {".", ".."} or re.fullmatch(r"[A-Za-z0-9_-]+", part) is None
        for part in parts
    ):
        raise ValueError(f"Invalid wiki page slug: {slug!r}")
    return _pages_dir().joinpath(*parts).with_suffix(".md")


def list_pages() -> list[str]:
    """Return all wiki page slugs (e.g. concepts/rag)."""
    root = _pages_dir()
    if not root.exists():
        return []
    return sorted(
        str(path.relative_to(root).with_suffix("")).replace("\\", "/")
        for path in root.rglob("*.md")
    )


class WikiStore:
    """Manage the on-disk markdown wiki."""

    @property
    def page_count(self) -> int:
        return len(list_pages())

    def get_page(self, slug: str) -> WikiPage | None:
        path = _slug_to_path(slug)
        if not path.exists():
            return None

        raw_text = path.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(raw_text)
        title = meta.get("title") or slug.split("/")[-1].replace("-", " ").title()
        tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]

        return WikiPage(
            slug=slug,
            title=title,
            content=body.strip(),
            raw_text=raw_text,
            source=meta.get("source"),
            tags=tags or None,
        )

    def write_page(
        self,
        slug: str,
        title: str,
        content: str,
        *,
        source: str | None = None,
        tags: list[str] | None = None,
    ) -> Path:
        path = _slug_to_path(slug)
        path.parent.mkdir(parents=True, exist_ok=True)

        lines = ["---", f'title: "{title}"']
        if source:
            lines.append(f'source: "{source}"')
        if tags:
            lines.append(f'tags: "{", ".join(tags)}"')
        lines.extend(["---", "", content.strip(), ""])

        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def search(self, query: str, top_k: int = 3) -> list[tuple[WikiPage, float]]:
        """
        Keyword search over wiki pages (no embeddings).

        Scores pages by term overlap in title, tags, and body.
        """
        if not query.strip():
            raise ValueError("query must not be empty")
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        query_terms = {
            term
            for term in re.findall(r"[A-Za-z0-9]+", query.lower())
            if len(term) > 2 and term not in _SEARCH_STOP_WORDS
        }
        if not query_terms:
            return []

        scored: list[tuple[WikiPage, float]] = []
        for slug in list_pages():
            page = self.get_page(slug)
            if not page:
                continue

            title_terms = set(re.findall(r"[A-Za-z0-9]+", page.title.lower()))
            body_terms = set(re.findall(r"[A-Za-z0-9]+", page.content.lower()))
            tag_terms = {t.lower() for t in (page.tags or [])}

            title_hits = len(query_terms & title_terms)
            tag_hits = len(query_terms & tag_terms)
            body_hits = len(query_terms & body_terms)

            score = title_hits * 3.0 + tag_hits * 2.0 + body_hits * 1.0
            if score > 0:
                scored.append((page, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]


wiki_store = WikiStore()
