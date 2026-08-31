"""Compile raw documents into the Open Wiki."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import settings
from src.wiki.pipeline import compile_directory, compile_sample_docs


def main() -> None:
    raw_dir = Path(settings.sample_docs_dir)
    if not raw_dir.exists():
        print(f"Sample docs directory not found: {raw_dir}")
        sys.exit(1)

    print(f"Compiling documents from {raw_dir} into Open Wiki...")
    results = compile_sample_docs()

    if not results:
        print("No .txt or .md files found.")
        sys.exit(1)

    for source, slug in results.items():
        print(f"  {source} -> wiki/{slug}.md")

    print(f"\nDone. {len(results)} page(s) compiled.")
    print(f"Wiki location: {settings.wiki_pages_dir}")


if __name__ == "__main__":
    main()
