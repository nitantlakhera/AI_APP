"""Ingest sample documents into the vector database."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import settings
from src.rag.pipeline import ingest_directory


def main() -> None:
    docs_dir = Path(settings.sample_docs_dir)
    print(f"Ingesting documents from: {docs_dir}")
    results = ingest_directory(docs_dir)
    if results:
        for name, count in results.items():
            print(f"  {name}: {count} chunks")
        print(f"\nDone! Total files: {len(results)}")
    else:
        print("No .txt or .md files found.")


if __name__ == "__main__":
    main()
