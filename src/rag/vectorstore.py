"""Vector store using ChromaDB."""

from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from src.config import settings
from src.rag.embeddings import embed_texts, embed_query


class VectorStore:
    """
    Stores document chunks as vectors for similarity search.

    Concept: Vector Database
    - Documents are split into chunks, embedded, and stored
    - Queries are embedded and matched against stored vectors
    - Returns the most semantically similar chunks
    """

    COLLECTION_NAME = "learning_docs"

    def __init__(self) -> None:
        persist_dir = Path(settings.chroma_persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)

        self._client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def document_count(self) -> int:
        return self._collection.count()

    def add_documents(
        self,
        texts: list[str],
        metadatas: list[dict] | None = None,
        ids: list[str] | None = None,
    ) -> int:
        """Add text chunks to the vector store."""
        if not texts:
            return 0

        embeddings = embed_texts(texts)
        doc_ids = ids or [f"doc_{i}" for i in range(self._collection.count(), self._collection.count() + len(texts))]
        meta = metadatas or [{"source": "unknown"} for _ in texts]

        self._collection.upsert(
            documents=texts,
            embeddings=embeddings,
            metadatas=meta,
            ids=doc_ids,
        )
        return len(texts)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Find the most relevant document chunks for a query."""
        if not query.strip():
            raise ValueError("query must not be empty")
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")
        if self._collection.count() == 0:
            return []

        query_embedding = embed_query(query)
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self._collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        for i in range(len(results["documents"][0])):
            chunks.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "relevance": round(1 - results["distances"][0][i], 3),
            })
        return chunks

    def clear(self) -> None:
        """Remove all documents."""
        self._client.delete_collection(self.COLLECTION_NAME)
        self._collection = self._client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )


# Singleton
vector_store = VectorStore()
