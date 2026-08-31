# AI Concepts Explained

A beginner-friendly guide to every AI concept in this project.

---

## 1. Generative AI

**What:** AI systems that create new content (text, images, code) rather than just classifying input.

**How it works in this project:**
- The `LLMProvider` class (`src/llm/provider.py`) sends your messages to a language model
- The model predicts the next token repeatedly to generate a full response
- Supports Ollama (local), OpenAI (cloud), and demo mode

**Key idea:** The model doesn't "know" things — it predicts statistically likely text based on patterns learned during training.

**Try it:** Chat tab → ask any question

---

## 2. Chat Application

**What:** A multi-turn conversation interface where the AI remembers previous messages.

**How it works:**
- `ChatSession` (`src/chat/service.py`) stores all messages in a list
- Each new message includes the full history (system prompt + all prior turns)
- The LLM uses this context to give coherent, contextual replies

**Key idea:** The "context window" is the model's short-term memory. Older messages may be trimmed to fit.

**Try it:** Chat tab → have a multi-turn conversation ("My name is Alex" → "What's my name?")

---

## 3. Prompt Engineering

**What:** Crafting instructions that guide the LLM's behavior and output quality.

**Types of prompts in this project:**
- **System prompt** — Sets the AI's role and rules (in every module)
- **RAG prompt** — Includes retrieved context before the question
- **Agent prompt** — Tells the agent what tools are available and how to use them

**Key idea:** Small changes to prompts can dramatically change output quality. This is one of the most impactful skills in AI engineering.

**Try it:** Edit the `system_prompt` in `ChatSession` and see how responses change.

---

## 4. RAG (Retrieval Augmented Generation)

**What:** A technique that searches your documents for relevant information, then includes that information in the LLM prompt to generate grounded answers.

**The pipeline:**
```
Question → Embed Query → Search Vector DB → Retrieve Top Chunks
    → Build Prompt with Context → LLM Generates Answer
```

**Why it matters:**
- LLMs have a knowledge cutoff — RAG gives them current/private data
- Can reduce hallucination by grounding answers, but does not guarantee correctness
- Answers are traceable to source documents

**Files:** `src/rag/pipeline.py`, `src/rag/embeddings.py`, `src/rag/vectorstore.py`

**Try it:** RAG tab → ingest docs → ask "What is RAG?"

---

## 4b. Open Wiki (Alternative to RAG)

**What:** This project provides a simplified teaching implementation inspired
by [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
It stores one markdown topic page per source and retrieves pages with weighted
keyword matching.

**RAG vs Open Wiki:**

| | RAG | Open Wiki |
|---|---|---|
| Storage | Vector chunks in ChromaDB | Markdown files on disk |
| Retrieval | Embedding similarity | Weighted title/tag/body keywords |
| Knowledge | Raw chunks selected each query | Persistent page replaced on recompile |
| Human readable | Hidden in vector DB | Full wiki you can browse in any editor |

**The pipeline:**
```
Raw docs → demo conversion or LLM → one markdown page per source
Question → keyword page search → read page content → LLM generates answer
```

**Why it matters:**
- Pages persist on disk and can be inspected or version controlled
- Git-friendly — wiki pages are plain markdown you own
- No vector database required — simpler stack for personal knowledge bases
- Great for learning the trade-off between RAG and wiki-style knowledge management

**Important limitation:** This demo does not perform cross-document synthesis,
entity maintenance, contradiction detection, wikilink traversal, or autonomous
updates. Those capabilities belong to fuller LLM Wiki systems.

**Files:** `src/wiki/store.py`, `src/wiki/pipeline.py`, `data/wiki/pages/`

**Try it:** Open Wiki tab → ask "What is the difference between RAG and Open Wiki?" → compare with the same question in the RAG tab

---

## 5. Embeddings

**What:** Converting text into vectors (lists of numbers) that capture semantic meaning.

**How it works:**
- "Dog" and "puppy" produce similar vectors (close in vector space)
- "Dog" and "airplane" produce very different vectors (far apart)
- This enables **semantic search** — finding by meaning, not just keywords

**In this project:**
- Model: `all-MiniLM-L6-v2` (384 dimensions, runs locally)
- Library: `sentence-transformers`

**Try it:** Ingest docs, then search for "neural networks" — it will find chunks about embeddings and transformers even if those exact words aren't in the query.

---

## 6. Vector Database

**What:** A database optimized for storing and searching embedding vectors.

**In this project:**
- ChromaDB stores document chunks as vectors
- Cosine similarity finds the closest matches
- Data persists in `data/chroma_db/`

**Alternatives:** Pinecone, Weaviate, FAISS, pgvector

**Try it:** Check the sidebar for "Docs indexed: X chunks" after ingesting.

---

## 7. AI Agents (Agentic AI)

**What:** An LLM that autonomously decides what actions to take to accomplish a goal, using tools in a loop.

**Generative AI vs Agentic AI:**
| | Generative AI | Agentic AI |
|---|---|---|
| Input | Prompt | Goal/task |
| Output | Text/content | Actions + results |
| Behavior | One-shot generation | Multi-step reasoning loop |

**The ReAct loop:**
```
User: "What's 15*23 and the weather in Tokyo?"
  → Agent thinks: "I need the calculator"
  → Calls calculator("15*23") → 345
  → Agent thinks: "Now I need weather"
  → Calls get_weather("Tokyo") → 28°C, Humid
  → Agent synthesizes: "15×23 = 345. Tokyo is 28°C and humid."
```

**Files:** `src/agents/agent.py`, `src/agents/tools.py`

**Try it:** Agent tab → "What is 100 / 4 + sqrt(81)?"

---

## 8. Tool Calling / Function Calling

**What:** The LLM outputs structured JSON requesting a specific function call, instead of just text.

**Example:**
```json
{
  "tool": "calculator",
  "arguments": {"expression": "2 + 2"}
}
```

The application executes the function and feeds the result back to the LLM.

**Available tools in this project:**
| Tool | What It Does |
|------|-------------|
| `calculator` | Evaluates math expressions |
| `get_weather` | Returns mock weather data |
| `get_current_time` | Returns current date/time |
| `search_knowledge` | Searches the RAG knowledge base |
| `search_wiki` | Searches the Open Wiki pages |

**Try it:** Agent tab → ask a math question and watch the tool call in the reasoning steps.

---

## 9. MCP (Model Context Protocol)

**What:** An open standard for connecting AI models to external tools, data sources, and services.

**Analogy:** MCP is like USB for AI — one standard protocol, many compatible devices.

**How it works:**
- **MCP Server** — Exposes tools and data (our `src/mcp/server.py`)
- **MCP Client** — AI application that connects to servers (Cursor, Claude Desktop)
- **Transport** — Communication via stdio, HTTP, or SSE

**In this project:**
- Run `python -m src.mcp.server` to start the server
- It exposes: calculator, weather, time, and RAG search
- Connect from Cursor or Claude Desktop via MCP config

**Why it matters:** Instead of every AI app building custom integrations, MCP provides one standard way to add capabilities.

---

## 10. How It All Fits Together

```
You (Student)
    │
    ▼
Streamlit UI ──── Chat ──── LLM generates text
    │              │
    │              └── Conversation memory
    │
    ├── RAG ──── Embed query → Search vectors → LLM + context
    │
    ├── Open Wiki ─ Search pages → Read compiled markdown → LLM + context
    │
    ├── Agent ── LLM decides → Call tool → Observe → Loop
    │
    └── MCP ──── External AI clients use our tools
```

Each concept builds on the previous one:
1. **Generative AI** — the foundation (LLM generates text)
2. **Chat** — adds memory (multi-turn context)
3. **RAG** — adds knowledge via vector retrieval (search your docs)
4. **Open Wiki** — adds knowledge via compiled markdown pages (alternative to RAG)
5. **Agents** — adds action (use tools autonomously)
6. **MCP** — adds interoperability (standard tool protocol)
7. **Fine-Tuning (LoRA)** — specializes model weights for your task (`fine_tuning/`)

---

## What's Next?

This project covers the **core foundations**. For expert-level topics not covered here (multi-agent systems, RLHF, production deployment, multimodal AI, and more), see:

**[Advanced Concepts & Expert Roadmap](ADVANCED_CONCEPTS.md)**

For how to run and use the project, see **[How to Run and Use](RUN_AND_USE.md)**.

For an exact explanation of what is real, deterministic, mock, or simplified,
see **[Demo Project Accuracy Guide](DEMO_PROJECT_GUIDE.md)**.
