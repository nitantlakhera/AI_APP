"""Medical RAG — retrieve from health education documents."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from functools import lru_cache

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from medical_assistant.src.config import settings
from medical_assistant.src.llm_bridge import Message, llm

DISCLAIMER = (
    "[Educational information only — not medical advice. Consult a doctor for health concerns.]"
)


@lru_cache(maxsize=1)
def _embedding_model() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    return _embedding_model().encode(texts, show_progress_bar=False).tolist()


def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]


class MedicalVectorStore:
    """ChromaDB store for medical education documents."""

    def __init__(self) -> None:
        persist_dir = Path(settings.chroma_persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=settings.collection_name,
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
        if not texts:
            return 0
        embeddings = embed_texts(texts)
        start = self._collection.count()
        doc_ids = ids or [f"med_{start + i}" for i in range(len(texts))]
        meta = metadatas or [{"source": "unknown"} for _ in texts]
        self._collection.upsert(documents=texts, embeddings=embeddings, metadatas=meta, ids=doc_ids)
        return len(texts)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if not query.strip():
            raise ValueError("query must not be empty")
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")
        if self._collection.count() == 0:
            return []
        results = self._collection.query(
            query_embeddings=[embed_query(query)],
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


vector_store = MedicalVectorStore()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between zero and chunk_size - 1")
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start += chunk_size - overlap
    return chunks


def ingest_file(file_path: Path) -> int:
    text = file_path.read_text(encoding="utf-8")
    chunks = chunk_text(text)
    metadatas = [{"source": file_path.name, "chunk_index": i} for i in range(len(chunks))]
    ids = [f"{file_path.stem}_{i}" for i in range(len(chunks))]
    return vector_store.add_documents(chunks, metadatas=metadatas, ids=ids)


def ingest_directory(directory: Path) -> dict[str, int]:
    results = {}
    for pattern in ("*.txt", "*.md"):
        for file_path in directory.glob(pattern):
            results[file_path.name] = ingest_file(file_path)
    return results


RAG_PROMPT = """You are a medical education assistant. Answer using ONLY the context below.
This is for LEARNING — not real medical advice. Always add: consult a doctor for health concerns.

Context:
{context}
"""


def medical_rag_query(question: str, top_k: int = 3) -> dict:
    if not question.strip():
        raise ValueError("question must not be empty")
    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    chunks = vector_store.search(question, top_k=top_k)
    if not chunks:
        return {
            "answer": "No medical documents indexed. Run ingest or click 'Ingest Medical Docs' in the RAG tab.",
            "sources": [],
            "chunks": [],
        }

    context = "\n\n".join(
        f"[{i}] (from {c['metadata'].get('source', '?')})\n{c['text']}"
        for i, c in enumerate(chunks, 1)
    )
    messages = [
        Message(role="system", content=RAG_PROMPT.format(context=context)),
        Message(role="user", content=question),
    ]
    response = llm.chat(messages, temperature=0.3)

    answer = response.content
    if llm.is_demo_mode and chunks:
        answer = (
            "[Demo Mode — retrieved medical education context]\n\n"
            + "\n\n---\n\n".join(
                f"**{c['metadata'].get('source')}** (relevance: {c['relevance']})\n{c['text'][:280]}..."
                for c in chunks
            )
            + f"\n\n{DISCLAIMER}"
        )
    else:
        answer = f"{answer}\n\n{DISCLAIMER}"

    return {
        "answer": answer,
        "sources": sorted({c["metadata"].get("source", "?") for c in chunks}),
        "chunks": chunks,
    }
