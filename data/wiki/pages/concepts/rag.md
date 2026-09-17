---
title: "Rag"
source: "02_rag.txt"
tags: "compiled"
---

RAG — Retrieval Augmented Generation
=====================================

### What is RAG?
RAG is a technique that combines information retrieval with text generation, allowing for more accurate and relevant answers by incorporating relevant information from documents and generating answers grounded in actual data.

### Why Use RAG?
RAG offers several advantages, including:

* **Grounding answers in real data**: RAG uses actual documents to generate answers, reducing the risk of hallucinations or misinformation.
* **Using proprietary/private data**: RAG can be used with proprietary or private data without retraining the model, making it a more efficient and flexible solution.
* **Traceable answers**: The use of source documents ensures that answers can be traced back to their original sources.

### The RAG Pipeline
The RAG pipeline consists of the following steps:

#### 1. INGEST
Load documents, split into chunks, and create embeddings.

#### 2. STORE
Save embeddings in a vector database (e.g., ChromaDB, Pinecone).

#### 3. RETRIEVE
When a question is asked, embed the query and find similar chunks in the vector database.

#### 4. AUGMENT
Add retrieved chunks to the LLM prompt as context.

#### 5. GENERATE
The LLM produces an answer based on the provided context.

### Key Components
#### Embeddings
Convert text to vectors that capture meaning.

#### Vector Database
Stores and searches embeddings efficiently.

#### Chunking
Split long documents into smaller pieces for better retrieval.

#### Reranking
Optionally re-score results for better relevance.

### Best Practices
* **Chunk size**: Use chunks of 300-1000 tokens with 10-20% overlap.
* **Metadata**: Use source, date, and author metadata for filtering.
* **Evaluation**: Separate evaluation of retrieval quality from generation quality.
* **Hybrid search**: Consider hybrid search (keyword + semantic) for better results.
