---
title: "Embeddings"
source: "04_embeddings.txt"
tags: "compiled"
---

## Embeddings and Vector Databases
================================

### What are Embeddings?

An embedding is a list of numbers (a vector) that represents the meaning of text. Similar texts have similar vectors — "dog" and "puppy" are close together, while "dog" and "airplane" are far apart.

### How Embeddings Work

1. A neural network (sentence-transformer) reads the text, outputs a fixed-size vector (e.g., 384 numbers), capturing semantic meaning, not just words.
2. The vector captures the meaning of the text, not the words themselves.

### Example with all-MiniLM-L6-v2

* Input: "What is machine learning?"
* Output: [0.12, -0.45, 0.78, ... ] (384 dimensions)

### Vector Databases

A vector database stores embeddings and enables fast similarity search. Instead of searching by exact keywords, you search by meaning.

#### Popular Vector Databases

- **ChromaDB**: Simple, embedded, great for learning (used in this project)
- **Pinecone**: Managed cloud service, scales to billions of vectors
- **Weaviate**: Open source with hybrid search
- **FAISS**: Facebook's library, very fast, no server needed

### Similarity Metrics

- **Cosine Similarity**: Measures angle between vectors (most common)
- **Euclidean Distance**: Straight-line distance between vectors
- **Dot Product**: Simple but affected by vector magnitude

#### In This Project

- **Model**: all-MiniLM-L6-v2 (384 dimensions, runs locally)
- **Database**: ChromaDB (persists to data/chroma_db/)
- **Search**: Cosine similarity, returns top-k most relevant chunks
