# AI Learning Lab

A beginner-friendly project to learn **Generative AI** and **Agentic AI** concepts by building and running real code.

> Start with [Demo Project: What Is Real and What Is Simplified](docs/DEMO_PROJECT_GUIDE.md)
> so you can distinguish complete implementations from educational shortcuts.

## What You'll Learn

| Concept | What It Is | Where in Code |
|---------|-----------|---------------|
| **Generative AI** | LLMs that create text | `src/llm/`, `src/chat/` |
| **Chat Application** | Multi-turn conversations with memory | `src/chat/service.py` |
| **Prompt Engineering** | System prompts that guide behavior | All modules |
| **RAG** | Search docs + generate grounded answers | `src/rag/` |
| **Open Wiki** | Compiled markdown knowledge base (alternative to RAG) | `src/wiki/` |
| **Embeddings** | Text → vectors for semantic search | `src/rag/embeddings.py` |
| **Vector Database** | Store & search embeddings | `src/rag/vectorstore.py` |
| **AI Agents** | LLM that decides to use tools | `src/agents/agent.py` |
| **Tool Calling** | LLM requests external functions | `src/agents/tools.py` |
| **MCP** | Standard protocol for AI tools | `src/mcp/server.py` |

## Quick Start

> **Full run & use guide:** [docs/RUN_AND_USE.md](docs/RUN_AND_USE.md) — step-by-step install, run, and use every feature.

### 1. Prerequisites

- Python 3.10+
- (Optional) [Ollama](https://ollama.com) for free local LLM

### 2. Install

```bash
cd AI_APP
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure

```bash
copy .env.example .env
```

**Option A — Ollama (free, recommended for students):**
```bash
# Install Ollama from https://ollama.com, then:
ollama pull llama3.2
```
Set in `.env`: `LLM_PROVIDER=ollama`

**Option B — OpenAI:**
Set in `.env`: `LLM_PROVIDER=openai` and add your `OPENAI_API_KEY`

**Option C — Demo mode (no LLM needed):**
Set in `.env`: `LLM_PROVIDER=demo`

### 4. Run

```bash
# Start the web app
python -m streamlit run app.py

# (Optional) Pre-load sample documents for RAG
python scripts/ingest.py

# (Optional) Compile sample docs into Open Wiki pages
python scripts/compile_wiki.py

# (Optional) Start MCP server for Cursor/Claude Desktop
python -m src.mcp.server
```

Open **http://localhost:8501** in your browser.

### 5. How to Use (Quick)

| Tab | What to do |
|-----|-----------|
| **Chat** | Type a message, press Enter — multi-turn conversation |
| **RAG** | Click "Ingest Sample Docs" → ask "What is RAG?" → see answer + sources |
| **Open Wiki** | Browse pre-built pages → ask "What is Open Wiki vs RAG?" → compare with RAG tab |
| **Agent** | Try "What is 25 * 17?" → watch it use the calculator tool |
| **Fine-Tune** | Train LoRA adapter → infer → compare base vs fine-tuned |
| **Concepts** | Read about each AI concept and see the integration diagram |

**Fine-tuning requires extra deps:** `pip install -r fine_tuning/requirements.txt`

See [docs/RUN_AND_USE.md](docs/RUN_AND_USE.md) for the complete walkthrough.

## Project Structure

```
AI_APP/
├── app.py                  # Streamlit web UI (start here!)
├── requirements.txt        # Python dependencies
├── .env.example            # Configuration template
│
├── src/
│   ├── config.py           # Settings from .env
│   ├── llm/
│   │   └── provider.py     # LLM abstraction (Ollama/OpenAI/Demo)
│   ├── chat/
│   │   └── service.py      # Chat with conversation memory
│   ├── rag/
│   │   ├── embeddings.py   # Text → vector conversion
│   │   ├── vectorstore.py  # ChromaDB vector database
│   │   └── pipeline.py     # Full RAG: retrieve → augment → generate
│   ├── wiki/
│   │   ├── store.py        # Markdown wiki pages (read, search, write)
│   │   └── pipeline.py     # Compile docs → wiki, query wiki pages
│   ├── agents/
│   │   ├── tools.py        # Calculator, weather, search tools
│   │   └── agent.py        # ReAct agent loop
│   └── mcp/
│       └── server.py       # MCP server (stdio)
│
├── data/
│   ├── sample_docs/        # Learning documents for RAG
│   └── wiki/pages/         # Compiled Open Wiki (markdown)
│
├── scripts/
│   ├── ingest.py           # Load docs into vector DB
│   └── compile_wiki.py     # Compile docs into Open Wiki pages
│
└── docs/
    ├── GETTING_STARTED.md  # Step-by-step setup guide
    ├── CONCEPTS.md         # Detailed concept explanations
    ├── architecture.md     # Architecture diagrams
    └── images/             # PNG diagrams (LLM, pipelines, integration)
```

## Architecture

**Visual diagrams (PNG):**

| Diagram | What it shows |
|---------|---------------|
| [LLM Architecture](docs/images/llm-architecture.png) | Shared LLM provider for Chat, RAG, Agent, Fine-Tune |
| [Pipeline Structure](docs/images/pipeline-structure.png) | Step-by-step flows for each feature |
| [System Integration](docs/images/integration-overview.png) | Main app, MCP, Medical Assistant |

Open [docs/html/index.html](docs/html/index.html) in your browser for interactive learning flows + diagrams.

See [Integration Diagram](docs/INTEGRATION_DIAGRAM.md) for how Chat, RAG, Agents, and MCP connect together.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MAIN INTEGRATED PRODUCT (app.py)                    │
│                                                                      │
│   Chat Tab ──► chat/service ──┐                                     │
│   RAG Tab  ──► rag/pipeline ──┼──► LLM Provider ──► Ollama/OpenAI  │
│   Agent Tab ─► agents/agent ──┘         ▲                           │
│                              │          │                           │
│                              └── tools/search_knowledge ──► RAG     │
│                                                                      │
│   MCP Server (separate process) ──► same tools + rag_search ──► RAG  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  INTEGRATED MODULE: fine_tuning/ (main tab + standalone LoRA app)   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│    DOMAIN APP: medical_assistant/ (Healthcare — Chat,RAG,Agent,MCP) │
└─────────────────────────────────────────────────────────────────────┘
```

See [docs/ARCHITECTURE_GUIDE.md](docs/ARCHITECTURE_GUIDE.md) for detailed diagrams.

## Learning Path

1. **Start with Chat** — Talk to the LLM, understand prompts and context
2. **Try RAG** — Ingest sample docs, ask questions, see retrieval in action
3. **Try Open Wiki** — Browse compiled pages, compare same questions with RAG
4. **Use the Agent** — Ask it to calculate, check weather, search docs or wiki
4. **Read the Code** — Each file has comments explaining the concept
5. **Explore MCP** — Connect the MCP server to Cursor or Claude Desktop
6. **Read Docs** — [docs/CONCEPTS.md](docs/CONCEPTS.md) for deep dives

## Documentation

- **[HTML Learning Flows](docs/html/index.html)** — open in browser, step-by-step visual guides
- **[Demo Accuracy Guide](docs/DEMO_PROJECT_GUIDE.md)** — exact behavior, limitations, and correct conclusions
- **[How to Run and Use](docs/RUN_AND_USE.md)** — install, run, and use every feature (start here!)
- [User Guide](docs/USER_GUIDE.md) — complete guide to using the app
- [Integration Diagram](docs/INTEGRATION_DIAGRAM.md) — how Chat, RAG, Agent & MCP connect
- [Architecture Guide](docs/ARCHITECTURE_GUIDE.md) — system design and components
- [Call Flow Guide](docs/CALL_FLOW_GUIDE.md) — step-by-step request flows
- [Getting Started Guide](docs/GETTING_STARTED.md) — quick setup checklist
- [AI Concepts Explained](docs/CONCEPTS.md) — concept deep dives
- [Advanced Concepts & Expert Roadmap](docs/ADVANCED_CONCEPTS.md) — topics not covered but needed for experts
- [LLM Fine-Tuning Lab](fine_tuning/README.md) — separate module for LoRA fine-tuning
- [Medical Assistant Lab](medical_assistant/README.md) — healthcare domain application (Chat, RAG, Agent, MCP)

## License

MIT — free for learning and experimentation.
