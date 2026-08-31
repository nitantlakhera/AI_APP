---
title: "Open Wiki vs RAG"
source: "compiled"
tags: "open-wiki, rag, knowledge-base, concepts"
---

## Summary

The full **LLM Wiki pattern** describes a persistent markdown knowledge base
maintained by an LLM. This project implements a smaller educational version:
each source is converted into one persistent markdown page, and questions use
weighted keyword search over those pages instead of vector retrieval.

## Why not just RAG?

Classic RAG retrieves document fragments on every query. Nothing accumulates — ask a question that synthesizes five documents and the LLM rediscovers the pieces every time.

In a full LLM Wiki, an agent can integrate a new source into existing topic and
entity pages, revise synthesis, and flag contradictions. **This demo does not
implement those maintenance features.** It writes or replaces one page per
source and refreshes a page index.

## Comparison

| | RAG | Open Wiki |
|---|-----|-----------|
| Persistent readable knowledge | Raw source remains; retrieval result is temporary | Yes — pages remain on disk |
| Cross-document synthesis | Fragment assembly at query time | Not implemented in this demo |
| Citations | Chunk references | Wikilinks to source pages |
| Storage | Vector database | Markdown files (Git-friendly) |
| Retrieval | Embedding similarity | Weighted title/tag/body keyword search |

## How it works in this project

- `src/wiki/store.py` — read, search, write markdown pages
- `src/wiki/pipeline.py` — compile raw docs → wiki pages, query wiki
- `data/wiki/pages/` — the compiled wiki (human-readable!)
- **Open Wiki tab** — browse, compile, and query

## When to use which

- **RAG**: large document corpora, need exact passage retrieval, private enterprise docs
- **This demo Wiki**: learning vector-free retrieval, browsing generated pages,
  and version-controlling notes
- **A full LLM Wiki**: personal knowledge bases with agent-maintained,
  cross-source synthesis (requires additional implementation)

## Related

- [[concepts/rag|RAG]]
- [[concepts/generative-ai|Generative AI]]
- [[index]]
