# Integration Diagram — How Everything Connects

This document shows how **Chat**, **RAG**, **Open Wiki**, **Agents**, **MCP**,
**Fine-Tuning**, and the **Medical Assistant** work together.

> **Current implementation note:** The main app has six top-level tabs: Chat,
> RAG, Open Wiki, Agent, Fine-Tune, and Concepts. Some large ASCII diagrams below
> emphasize the original RAG path to keep them readable. Open Wiki is a parallel
> path: `app.py → wiki/pipeline.py → wiki/store.py → data/wiki/pages/`, and is
> available to the Agent as `search_wiki` and to MCP as `wiki_search`.

> **PNG diagrams:** [LLM Architecture](images/llm-architecture.png) · [Pipeline Structure](images/pipeline-structure.png) · [System Integration](images/integration-overview.png)  
> Regenerate: `python scripts/generate_diagrams.py`

---

## 0. Repository Overview — Three Applications

| App | Folder | Type | Domain |
|-----|--------|------|--------|
| **AI Learning Lab** | `/` (root `app.py`) | Integrated product | General AI education |
| **Medical Assistant** | `medical_assistant/` | Integrated product | Healthcare education |
| **Fine-Tuning Lab** | `fine_tuning/` | In main app Fine-Tune tab + standalone |

```
AI_APP/
├── app.py                    ← Main lab (Chat, RAG, Wiki, Agent, Fine-Tune)
├── medical_assistant/app.py  ← Healthcare lab (same architecture)
└── fine_tuning/app.py        ← LoRA training (standalone)
```

See [medical_assistant/docs/INTEGRATION_DIAGRAM.md](../medical_assistant/docs/INTEGRATION_DIAGRAM.md) for medical app details.

---

## 1. Big Picture — One Product, Two Modules

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI LEARNING LAB (AI_APP)                            │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │              MAIN INTEGRATED PRODUCT  (app.py)                        │  │
│  │                                                                       │  │
│  │   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌──────────┐           │  │
│  │   │  CHAT   │   │   RAG   │   │  AGENT  │   │ CONCEPTS │           │  │
│  │   │  Tab    │   │  Tab    │   │  Tab    │   │   Tab    │           │  │
│  │   └────┬────┘   └────┬────┘   └────┬────┘   └──────────┘           │  │
│  │        │             │             │                                  │  │
│  │        ▼             ▼             ▼                                  │  │
│  │   chat/service   rag/pipeline   agents/agent                         │  │
│  │        │             │             │                                  │  │
│  │        │             │        agents/tools ◄── search_knowledge ──┐ │  │
│  │        │             │             │                               │ │  │
│  │        └─────────────┼─────────────┘                               │ │  │
│  │                      │                                             │ │  │
│  │                      ▼                                             │ │  │
│  │              ┌───────────────┐                                     │ │  │
│  │              │  LLM Provider │ ◄── shared by Chat, RAG, Agent     │ │  │
│  │              │  (src/llm/)   │                                     │ │  │
│  │              └───────┬───────┘                                     │ │  │
│  │                      │                                             │ │  │
│  │         ┌────────────┼────────────┐                                │ │  │
│  │         ▼            ▼            ▼                                │ │  │
│  │    Ollama API   OpenAI API   Demo Mode                            │ │  │
│  │                                                                     │ │  │
│  │   RAG DATA LAYER (shared by RAG tab + Agent + MCP):                │ │  │
│  │   ┌────────────┐    ┌────────────┐    ┌──────────────┐            │ │  │
│  │   │ Embeddings │───►│  ChromaDB  │◄───│ Sample Docs  │            │ │  │
│  │   │ (vectors)  │    │ (vectors)  │    │ data/sample/ │            │ │  │
│  │   └────────────┘    └─────┬──────┘    └──────────────┘            │ │  │
│  │                           │                                        │ │  │
│  │                           └────────────────────────────────────────┘ │  │
│  │                                                                       │  │
│  │   MCP SERVER (separate process, same codebase):                      │  │
│  │   ┌─────────────────────────────────────────────────────────────┐   │  │
│  │   │  src/mcp/server.py  ◄── stdio ──►  Cursor / Claude Desktop   │   │  │
│  │   │  Tools: calc, weather, time, rag_search ──► rag/pipeline    │   │  │
│  │   └─────────────────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │         INTEGRATED + STANDALONE MODULE  (fine_tuning/)                 │  │
│  │         Used by main Fine-Tune tab and fine_tuning/app.py             │  │
│  │                                                                       │  │
│  │   fine_tuning/app.py ──► trainer.py ──► LoRA adapter ──► inference   │  │
│  │                              │                                        │  │
│  │                         sample_dataset.jsonl                          │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Mermaid — Full Integration Map

```mermaid
graph TB
    subgraph UI["Main App — app.py (Integrated Product)"]
        CHAT_TAB[💬 Chat Tab]
        RAG_TAB[📚 RAG Tab]
        WIKI_TAB[📖 Open Wiki Tab]
        AGENT_TAB[🤖 Agent Tab]
        FT_TAB[🎯 Fine-Tune Tab]
        CONCEPTS_TAB[📖 Concepts Tab]
    end

    subgraph SERVICES["Shared Services — src/"]
        CHAT_SVC[chat/service.py<br/>Conversation Memory]
        RAG_PIPE[rag/pipeline.py<br/>Retrieve → Augment → Generate]
        WIKI_PIPE[wiki/pipeline.py<br/>Compile → Search Pages → Generate]
        WIKI_STORE[wiki/store.py<br/>Markdown Page Store]
        AGENT[agents/agent.py<br/>ReAct Loop]
        TOOLS[agents/tools.py<br/>calculator, mock weather, time,<br/>search_knowledge, search_wiki]
        LLM[llm/provider.py<br/>Ollama / OpenAI / Demo]
    end

    subgraph DATA["Shared Data Layer"]
        EMB[rag/embeddings.py]
        VDB[(ChromaDB<br/>data/chroma_db)]
        DOCS[sample_docs/<br/>.txt files]
        WIKI_PAGES[(data/wiki/pages/<br/>Markdown)]
    end

    subgraph MCP_LAYER["MCP — Separate Process"]
        MCP_SRV[mcp/server.py]
        MCP_CLIENT[Cursor / Claude Desktop]
    end

    subgraph FT["Fine-Tuning Implementation — fine_tuning/"]
        FT_UI[fine_tuning/app.py]
        FT_TRAIN[trainer.py + LoRA]
        FT_DATA[sample_dataset.jsonl]
    end

    subgraph EXTERNAL["External LLM Backends"]
        OLLAMA[Ollama]
        OPENAI[OpenAI API]
    end

    CHAT_TAB --> CHAT_SVC
    RAG_TAB --> RAG_PIPE
    WIKI_TAB --> WIKI_PIPE
    AGENT_TAB --> AGENT
    FT_TAB --> FT_TRAIN
    CONCEPTS_TAB -.-> CHAT_SVC & RAG_PIPE & AGENT

    CHAT_SVC --> LLM
    RAG_PIPE --> LLM
    WIKI_PIPE --> LLM
    RAG_PIPE --> EMB --> VDB
    WIKI_PIPE --> WIKI_STORE --> WIKI_PAGES
    DOCS --> WIKI_PIPE
    DOCS --> VDB

    AGENT --> LLM
    AGENT --> TOOLS
    TOOLS -->|search_knowledge| RAG_PIPE
    TOOLS -->|search_wiki| WIKI_PIPE

    LLM --> OLLAMA
    LLM --> OPENAI

    MCP_CLIENT <-->|stdio JSON-RPC| MCP_SRV
    MCP_SRV --> TOOLS
    MCP_SRV -->|rag_search| RAG_PIPE
    MCP_SRV -->|wiki_search| WIKI_PIPE

    FT_UI --> FT_TRAIN
    FT_DATA --> FT_TRAIN

    style UI fill:#e8f4fd
    style SERVICES fill:#fff3e0
    style DATA fill:#e8f5e9
    style MCP_LAYER fill:#f3e5f5
    style FT fill:#fce4ec
```

---

## 3. How Features Connect (Integration Points)

### 3.1 Shared LLM Provider

**All three main features use the same brain:**

```
                    ┌─────────────────────┐
                    │   llm/provider.py   │
                    │   (single instance) │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
    chat/service.py      rag/pipeline.py     agents/agent.py
    (conversation)       (grounded answers)  (tool decisions)
```

| Feature | Calls LLM? | Purpose |
|---------|-----------|---------|
| Chat | Yes | Generate conversational replies |
| RAG | Yes | Generate answer from retrieved context |
| Agent | Yes (per step) | Decide tools + synthesize final answer |

---

### 3.2 RAG Shared by Three Entry Points

**One RAG pipeline, three ways to use it:**

```
                         rag/pipeline.py
                         (rag_query function)
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
   RAG Tab (UI)      Agent search_knowledge    MCP rag_search
   app.py            agents/tools.py           mcp/server.py
         │                     │                     │
   User clicks          Agent decides to          External AI
   "Search & Answer"    search docs               client calls tool
```

**Flow when Agent searches docs:**
```
User: "Search the docs: what is RAG?"
  → Agent.run()
  → LLM decides: call search_knowledge
  → tools.search_knowledge("what is RAG?")
  → rag_query("what is RAG?")        ← same function as RAG tab!
  → vector_store.search()
  → llm.chat(context + question)
  → result returned to agent
  → agent gives final answer
```

---

### 3.3 Agent Tools = MCP Tools (Shared Logic)

```
agents/tools.py                    mcp/server.py
┌──────────────────┐              ┌──────────────────┐
│ calculator()     │◄────────────►│ calc()           │
│ get_weather()    │◄────────────►│ weather()        │
│ get_current_time │◄────────────►│ current_time()   │
│ search_knowledge │◄────────────►│ rag_search()    │
└────────┬─────────┘              └────────┬─────────┘
         │                                  │
         ▼                                  ▼
   Agent Tab (in-app)              Cursor / Claude (external)
```

Same functions, different interfaces:
- **Agent tab:** LLM autonomously picks which tool to call
- **MCP server:** External client explicitly requests a tool

---

### 3.4 Complete User Journey (All Features Together)

```
Step 1: INGEST (RAG Tab)
  User clicks "Ingest Sample Docs"
  → ingest_directory() → ChromaDB now has 16 chunks

Step 2: CHAT (Chat Tab)
  User: "What topics can you help me with?"
  → ChatSession → LLM → general reply

Step 3: RAG (RAG Tab)
  User: "What is an AI agent?"
  → rag_query() → searches ChromaDB → LLM + context → grounded answer

Step 4: AGENT (Agent Tab)
  User: "What is 25*17 and search docs for what is MCP?"
  → Agent Step 1: calculator("25*17") → 425
  → Agent Step 2: search_knowledge("what is MCP") → rag_query() → RAG answer
  → Agent Step 3: synthesizes final answer

Step 5: MCP (External — Cursor)
  Developer connects MCP server
  → Calls rag_search("What is RAG?")
  → Same rag_query() pipeline as above
```

---

## 4. Data Flow Diagram

```mermaid
flowchart LR
    subgraph INPUT["User Input"]
        U1[Chat message]
        U2[RAG question]
        U3[Agent task]
        U4[MCP tool call]
    end

    subgraph PROCESS["Processing"]
        P1[ChatSession]
        P2[rag_query]
        P3[Agent loop]
        P4[MCP handler]
    end

    subgraph SHARED["Shared Components"]
        S1[LLM Provider]
        S2[ChromaDB]
        S3[Tool Functions]
    end

    subgraph OUTPUT["Response"]
        O1[Chat reply]
        O2[Answer + sources]
        O3[Answer + steps]
        O4[Tool result JSON]
    end

    U1 --> P1 --> S1 --> O1
    U2 --> P2 --> S2 --> S1 --> O2
    U3 --> P3 --> S1
    P3 --> S3 --> S2
    P3 --> O3
    U4 --> P4 --> S3 --> S2 --> O4
```

---

## 5. File-Level Connection Map

```
app.py
 │
 ├── imports chat/service.py ──────────────► llm/provider.py
 │
 ├── imports rag/pipeline.py ──────────────► rag/embeddings.py
 │                                        ► rag/vectorstore.py
 │                                        ► llm/provider.py
 │
 ├── imports agents/agent.py ──────────────► agents/tools.py
 │                                        ► llm/provider.py
 │                                              │
 │                                              └── search_knowledge()
 │                                                       │
 │                                                       ▼
 │                                              rag/pipeline.py  ◄── INTEGRATION
 │
 └── (separate process)
      src/mcp/server.py ───────────────────► agents/tools.py
                                           ► rag/pipeline.py  ◄── INTEGRATION

fine_tuning/  (standalone — not connected to above yet)
 ├── app.py
 ├── src/trainer.py
 ├── src/inference.py
 └── data/sample_dataset.jsonl
```

---

## 6. What Is Integrated vs Separate

| Component | Status | Connected To |
|-----------|--------|-------------|
| Chat | **Integrated** | LLM Provider |
| RAG | **Integrated** | LLM, ChromaDB, Embeddings |
| Agent | **Integrated** | LLM, Tools, RAG (via search_knowledge) |
| MCP | **Integrated** | Same tools + RAG as Agent |
| Fine-Tuning | **Integrated in main app** | Fine-Tune tab + `fine_tuning/` module |

---

## 7. ASCII — Simplified "How It Works Together"

```
         YOU (Student)
              │
              ▼
    ┌─────────────────────┐
    │   Streamlit app.py   │  ◄── ONE UI, ONE PRODUCT
    │  Chat│RAG│Agent│Docs │
    └─────────┬───────────┘
              │
    ┌─────────┴──────────────────────────────────┐
    │                                            │
    ▼                    ▼                       ▼
 CHAT uses           RAG uses                AGENT uses
 LLM only            LLM + ChromaDB          LLM + Tools
                                              │
                                              ├── calculator
                                              ├── weather
                                              ├── time
                                              └── search_knowledge ──► RAG pipeline
                                                                         (same as RAG tab!)

    ┌──────────────────────────────────────────────────────────────┐
    │  MCP Server (run separately: python -m src.mcp.server)     │
    │  Exposes same tools + RAG to Cursor / Claude Desktop       │
    └──────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────┐
    │  fine_tuning/ (separate: streamlit run fine_tuning/app.py) │
    │  Learn LoRA fine-tuning — not connected to main app yet      │
    └──────────────────────────────────────────────────────────────┘
```

---

## Related Documentation

- [Architecture Guide](ARCHITECTURE_GUIDE.md) — detailed component design
- [Call Flow Guide](CALL_FLOW_GUIDE.md) — step-by-step request flows
- [User Guide](USER_GUIDE.md) — how to use each feature
- [Fine-Tuning Architecture](../fine_tuning/docs/ARCHITECTURE.md) — separate module design
