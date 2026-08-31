---
title: "Wiki Index"
tags: "index"
---

# AI Learning Lab Wiki

A persistent markdown knowledge base. Unlike RAG, queries read topic pages
instead of retrieving raw vector chunks. Re-run compilation when source files change.

## Pages
- [[concepts/agents|Agents]]
- [[concepts/embeddings|Embeddings]]
- [[concepts/generative-ai|Generative Ai]]
- [[concepts/open-wiki|Open Wiki vs RAG]]
- [[concepts/rag|Rag]]

## RAG vs Open Wiki

| | RAG | Open Wiki |
|---|-----|-----------|
| Storage | Vector chunks | Markdown pages |
| Retrieval | Embedding similarity | Page search + read |
| Knowledge | Raw chunks selected each query | Persistent pages rebuilt on compile |
| Best for | Semantic passage retrieval | Browsable, curated topic pages |
