"""Embedding generation for RAG."""

from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from src.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load the sentence-transformer model (cached after first load).

    Concept: Embeddings
    - Text is converted to a vector (list of numbers)
    - Similar meanings → similar vectors
    - Enables semantic search (not just keyword matching)
    """
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Convert a list of texts into embedding vectors."""
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Embed a single search query."""
    return embed_texts([query])[0]
