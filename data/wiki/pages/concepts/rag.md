---
title: "Rag"
source: "02_rag.txt"
tags: "compiled"
---

## Summary
Demo mode converted `02_rag.txt` into a persistent wiki page without using an LLM. The source content is preserved below rather than being presented as AI-generated synthesis.

## Source Knowledge

# RAG — Retrieval Augmented Generation

## What is RAG?
RAG is a technique that combines information retrieval with text generation.
Instead of relying only on what the LLM learned during training, RAG:
1. Searches your documents for relevant information
2. Includes that information in the prompt
3. Generates an answer grounded in your actual data

Why Use RAG?
- LLMs have a knowledge cutoff date — they don't know recent events
- LLMs can hallucinate (make up facts) — RAG grounds answers in real documents
- You can use proprietary/private data without retraining the model
- Answers are traceable to source documents

The RAG Pipeline:
1. INGEST: Load documents, split into chunks, create embeddings
2. STORE: Save embeddings in a vector database (ChromaDB, Pinecone, etc.)
3. RETRIEVE: When a question comes in, embed it and find similar chunks
4. AUGMENT: Add retrieved chunks to the LLM prompt as context
5. GENERATE: The LLM produces an answer based on the provided context

Key Components:
- Embeddings: Convert text to vectors (numbers) that capture meaning
- Vector Database: Stores and searches embeddings efficiently
- Chunking: Split long documents into smaller pieces for better retrieval
- Reranking: Optionally re-score results for better relevance

Best Practices:
- Chunk size: 300-1000 tokens with 10-20% overlap
- Use metadata (source, date, author) for filtering
- Evaluate retrieval quality separately from generation quality
- Consider hybrid search (keyword + semantic) for better results

## Related
- [[index]]
