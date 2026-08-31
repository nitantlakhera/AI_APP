"""RAG pipeline — Retrieval Augmented Generation."""

from __future__ import annotations

from pathlib import Path

from src.llm.provider import Message, llm
from src.rag.vectorstore import vector_store


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks for better retrieval."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between zero and chunk_size - 1")
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def ingest_file(file_path: Path) -> int:
    """Read a file, chunk it, and store in the vector database."""
    text = file_path.read_text(encoding="utf-8")
    chunks = chunk_text(text)
    metadatas = [{"source": file_path.name, "chunk_index": i} for i in range(len(chunks))]
    ids = [f"{file_path.stem}_{i}" for i in range(len(chunks))]
    return vector_store.add_documents(chunks, metadatas=metadatas, ids=ids)


def ingest_directory(directory: Path) -> dict[str, int]:
    """Ingest all .txt and .md files from a directory."""
    results = {}
    for pattern in ("*.txt", "*.md"):
        for file_path in directory.glob(pattern):
            count = ingest_file(file_path)
            results[file_path.name] = count
    return results


RAG_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.
Use ONLY the context below to answer. If the answer is not in the context, say "I don't have that information in the documents."
Always cite which source document your answer comes from.

Context:
{context}
"""


def rag_query(question: str, top_k: int = 3) -> dict:
    """
    Full RAG pipeline: Retrieve → Augment → Generate.

    Steps:
    1. RETRIEVE: Search vector DB for relevant chunks
    2. AUGMENT: Build a prompt with retrieved context
    3. GENERATE: LLM produces an answer grounded in the context
    """
    if not question.strip():
        raise ValueError("question must not be empty")
    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    chunks = vector_store.search(question, top_k=top_k)

    if not chunks:
        return {
            "answer": "No documents indexed yet. Run the ingest script or use the RAG tab to load sample docs.",
            "sources": [],
            "chunks": [],
        }

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk["metadata"].get("source", "unknown")
        context_parts.append(f"[{i}] (from {source})\n{chunk['text']}")

    context = "\n\n".join(context_parts)
    messages = [
        Message(role="system", content=RAG_SYSTEM_PROMPT.format(context=context)),
        Message(role="user", content=question),
    ]

    response = llm.chat(messages, temperature=0.3)

    answer = response.content
    if llm.is_demo_mode and chunks:
        answer = (
            "[Demo Mode — showing retrieved context]\n\n"
            + "\n\n---\n\n".join(
                f"**Source: {c['metadata'].get('source', '?')}** (relevance: {c['relevance']})\n{c['text'][:300]}..."
                for c in chunks
            )
            + "\n\n_Set LLM_PROVIDER=ollama or openai for generated answers._"
        )

    return {
        "answer": answer,
        "sources": sorted({c["metadata"].get("source", "unknown") for c in chunks}),
        "chunks": chunks,
    }
