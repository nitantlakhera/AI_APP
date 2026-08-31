# Demo Project: What Is Real and What Is Simplified

Use this page as the accuracy guide for the AI Learning Lab. The project is
designed to make architecture visible; it is not a production AI platform.

## Three Runtime Modes

| Mode | Uses a real LLM? | Internet required? | Intended use |
|------|------------------|--------------------|--------------|
| Demo | No; deterministic rules | Only when the embedding model is first downloaded | Learn UI and call flow |
| Ollama | Yes; local model | Model installation/download only | Learn real generation locally |
| OpenAI | Yes; cloud API | Yes | Learn hosted generation |

The checked-in `.env` currently uses `LLM_PROVIDER=demo`. Demo output proves that
the application wiring works, but it does not demonstrate general language
understanding.

## What Each Application Actually Does

### Chat

`ChatSession` stores system, user, and assistant messages in memory and sends the
history to the configured provider.

- Demo mode recognizes a small set of patterns, including the name-memory exercise.
- Ollama/OpenAI use the full message history for model-generated replies.
- History is lost when the Streamlit session ends.

### RAG

RAG is fully implemented as:

```text
document → 500-character overlapping chunks
→ all-MiniLM-L6-v2 embeddings → ChromaDB

question → query embedding → cosine nearest chunks
→ context prompt → configured LLM
```

- Embedding and retrieval are real in every mode.
- Demo mode displays retrieved chunks instead of synthesizing an answer.
- Ollama/OpenAI generate an answer from those chunks.
- Retrieval relevance is `1 - cosine distance`; it is a ranking aid, not a
  calibrated probability.

### Open Wiki Demo

This is a **small teaching implementation inspired by the LLM Wiki pattern**:

```text
source → one persistent markdown page
question → weighted keyword search over title/tags/body
→ page context → configured LLM
```

- It does not use embeddings or ChromaDB.
- In demo mode, compilation preserves source content in markdown without
  pretending that an LLM synthesized it.
- With Ollama/OpenAI, one LLM-generated page is written per source.
- Recompiling the same source replaces its canonical page.
- It does **not** yet integrate facts across existing pages, detect
  contradictions, maintain entities, follow wikilinks during retrieval, or
  autonomously keep itself current. Those are features of fuller LLM Wiki
  systems, not this demo.

### Agent

The Agent sends the user goal plus tool schemas to the LLM, executes requested
tools, returns observations, and loops for at most five steps.

Available tools:

- `calculator`
- `get_weather` (mock data, not live weather)
- `get_current_time` (local machine time)
- `search_knowledge` (RAG)
- `search_wiki` (Open Wiki)

Demo mode uses keyword rules to demonstrate tool routing. A real provider decides
which tool to call; tool selection and answers can vary.

### MCP

The MCP server exposes direct tools over stdio:

- `calc`
- `weather`
- `current_time`
- `rag_search`
- `wiki_search`

MCP is the communication protocol. It is not an LLM and does not automatically
make tools autonomous; the connected MCP client decides how to use them.

### Fine-Tuning

The fine-tuning module demonstrates LoRA/PEFT training, inference, and comparison.
It has separate, heavier dependencies and is not required for the main app's
Chat/RAG/Wiki/Agent features.

The tiny sample dataset and short training run are educational. They do not
produce a production-quality model or prove general improvement. The evaluator
uses deterministic greedy decoding for a repeatable qualitative side-by-side
comparison; it does not calculate an accuracy score.

### Medical Assistant

The medical module demonstrates the same architecture in a health domain. Its
weather-like lookups and educational documents are examples, not clinical data.
It must not be used for diagnosis, treatment, emergencies, or medication decisions.

## Recommended Student Experiment

1. Keep `LLM_PROVIDER=demo`.
2. Run `python scripts/smoke_test.py`.
3. Run `python scripts/ui_smoke_test.py`.
4. Start `python -m streamlit run app.py`.
5. Ingest documents and ask “What is RAG?”
6. Ask the same question in Open Wiki.
7. Compare raw retrieved chunks with persistent topic pages.
8. Ask the Agent to search first the docs, then the wiki.
9. Switch to Ollama only after the deterministic flows are clear.

## Correct Conclusions

- RAG and Open Wiki are alternative **knowledge access designs**, not competing
  language models.
- RAG quality depends first on retrieval quality, then on generation quality.
- This Open Wiki demo proves persistent markdown storage and keyword page
  retrieval; it does not prove full autonomous knowledge maintenance.
- Demo mode verifies control flow, not model intelligence or answer quality.
- Fine-tuning changes model weights/adapters; RAG and Wiki provide external
  context without retraining the base model.

