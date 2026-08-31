# User Guide

A complete guide for using the **AI Learning Lab** — from first setup to exploring every feature.

---

## Table of Contents

1. [What Is This Project?](#1-what-is-this-project)
2. [Installation](#2-installation)
3. [Configuration](#3-configuration)
4. [Running the Application](#4-running-the-application)
5. [Using the Web Interface](#5-using-the-web-interface)
6. [Command-Line Tools](#6-command-line-tools)
7. [MCP Server Setup](#7-mcp-server-setup)
8. [Learning Exercises](#8-learning-exercises)
9. [Troubleshooting](#9-troubleshooting)
10. [FAQ](#10-faq)

---

## 1. What Is This Project?

AI Learning Lab is a hands-on project for students and beginners to learn:

- **Generative AI** — how LLMs create text
- **Chat applications** — multi-turn conversations with memory
- **RAG** — answering questions from your own documents
- **Open Wiki** — compiling documents into persistent, linked markdown knowledge
- **AI Agents** — LLMs that use tools autonomously
- **MCP** — connecting AI apps to external tools via a standard protocol

Everything runs locally in your browser with simple Python code you can read and modify.

---

## 2. Installation

### Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.10+ | 3.11+ |
| RAM | 4 GB | 8 GB+ |
| Disk space | 2 GB | 5 GB (for Ollama models) |

### Step-by-Step Install

```bash
# 1. Navigate to the project folder
cd C:\Users\nila0425\Downloads\AI_APP

# 2. Create a virtual environment (recommended)
python -m venv .venv

# 3. Activate it (Windows PowerShell)
.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create your config file
copy .env.example .env
```

**First-time note:** The first RAG query downloads an embedding model (~80 MB) from Hugging Face. This is normal and happens only once.

---

## 3. Configuration

All settings live in the `.env` file at the project root.

### LLM Provider Options

| Provider | Setting | Best For |
|----------|---------|----------|
| Demo | `LLM_PROVIDER=demo` | Exploring UI without any setup |
| Ollama | `LLM_PROVIDER=ollama` | Free local AI (recommended) |
| OpenAI | `LLM_PROVIDER=openai` | Cloud AI with API key |

### Demo Mode (Easiest — No Model Required)

```env
LLM_PROVIDER=demo
```

Works immediately. Uses rule-based responses so you can explore the app structure without installing Ollama or paying for an API.

### Ollama (Recommended for Students)

1. Install [Ollama](https://ollama.com)
2. Download a model:
   ```bash
   ollama pull llama3.2
   ```
3. Configure `.env`:
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   ```

### OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4o-mini
```

### Other Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Local embedding model for RAG |
| `CHROMA_PERSIST_DIR` | `./data/chroma_db` | Where vector data is stored |
| `WIKI_PAGES_DIR` | `./data/wiki/pages` | Where compiled Open Wiki pages are stored |
| `WIKI_RAW_DIR` | `./data/wiki/raw` | Optional location for raw wiki source material |
| `MAX_AGENT_STEPS` | `5` | Max reasoning steps for the agent |

---

## 4. Running the Application

### Start the Web App

```bash
python -m streamlit run app.py
```

Open your browser at: **http://localhost:8501**

### Pre-load Documents (Optional)

```bash
python scripts/ingest.py
```

This indexes the sample learning documents into the vector database before you use the RAG tab.

### Compile Open Wiki Pages (Optional)

```bash
python scripts/compile_wiki.py
```

This compiles the same sample documents into structured markdown pages under
`data/wiki/pages/`. Pre-built pages are included, so the Open Wiki tab can also
be explored without running this command.

### Start the MCP Server (Optional)

```bash
python -m src.mcp.server
```

Exposes tools to external AI clients like Cursor or Claude Desktop.

---

## 5. Using the Web Interface

The app has six tabs. Each one teaches a different AI concept.

### Sidebar

The left sidebar shows:

- **LLM Status** — Ollama connectivity, or whether an OpenAI key is configured
- **Learning Guides** — paths and commands for opening documentation
- **Provider** — current LLM setting
- **Docs indexed** — number of RAG chunks loaded
- **Wiki pages** — number of compiled markdown pages available

---

### Tab 1: Chat

**Concept:** Generative AI with conversation memory.

**How to use:**
1. Type a message in the chat input at the bottom
2. Press Enter
3. The assistant replies and remembers earlier messages

**Try these:**
- "Hello, my name is Alex."
- "What is my name?" (tests memory)
- "Explain generative AI in simple terms."

**What to observe:**
- Each turn sends the full conversation history to the LLM
- The system prompt (in `src/chat/service.py`) shapes the assistant's personality

**Buttons:**
- **Clear Chat** — resets the conversation (keeps system prompt)

---

### Tab 2: RAG (Retrieval Augmented Generation)

**Concept:** Answer questions using your own documents, not just the LLM's training data.

**How to use:**
1. Click **"Ingest Sample Docs"** (left column) — loads 4 learning documents
2. Type a question in the input (right column), e.g. "What is RAG?"
3. Click **"Search & Answer"**
4. Read the answer and expand **Retrieved Chunks** to see which document parts were used

**Try these questions:**
| Question | Expected Source |
|----------|----------------|
| "What is generative AI?" | `01_generative_ai.txt` |
| "What is RAG?" | `02_rag.txt` |
| "How do AI agents work?" | `03_agents.txt` |
| "What are embeddings?" | `04_embeddings.txt` |

**What to observe:**
- Relevance scores show how closely each chunk matches your question
- In demo mode, you see retrieved context directly
- With a real LLM, the answer is generated from that context

---

### Tab 3: Open Wiki

**Concept:** A persistent knowledge base compiled into linked markdown pages,
as an alternative to retrieving raw vector chunks on every question.

**How to use:**
1. Open the **Open Wiki** tab
2. Expand **Browse pages** to inspect the available compiled pages
3. Optionally click **Compile Sample Docs** to rebuild pages from `data/sample_docs/`
4. Enter a question such as "What is the difference between RAG and Open Wiki?"
5. Click **Query Wiki**
6. Expand **Matched Wiki Pages** to inspect the pages used

**What to observe:**
- RAG retrieves raw chunks by embedding similarity
- Open Wiki searches human-readable, synthesized markdown pages
- Each compiled page persists and is replaced when the same source is recompiled
- Pages remain available in `data/wiki/pages/` and can be version controlled

This demo compiles each source independently. It does not yet merge knowledge
across existing pages, detect contradictions, or maintain entities autonomously.

**Direct Python use:**

```python
from src.wiki.pipeline import compile_sample_docs, wiki_query

compile_sample_docs()
result = wiki_query("What is Open Wiki?")
print(result["answer"])
print(result["pages"])
```

**When to choose each approach:**
- Choose **RAG** for large corpora and precise passage retrieval
- Choose this **Open Wiki demo** for persistent, human-readable topic pages and
  simple keyword retrieval
- A full agent-maintained LLM Wiki needs additional cross-page synthesis and
  consistency logic not implemented here

---

### Tab 4: Agent

**Concept:** An AI that decides which tools to use and loops until it has an answer.

**How to use:**
1. Type a task or click one of the example buttons
2. Click **"Run Agent"**
3. Read the final answer
4. Expand **Reasoning Steps** to see which tools were called

**Example tasks:**

| Task | Tool Used | What Happens |
|------|-----------|--------------|
| "What is 25 * 17?" | `calculator` | Evaluates math |
| "What's the weather in London?" | `get_weather` | Returns mock weather |
| "What time is it?" | `get_current_time` | Returns current datetime |
| "Search the docs: what is RAG?" | `search_knowledge` | Runs RAG pipeline |
| "Search the wiki: what is Open Wiki?" | `search_wiki` | Runs Open Wiki query |

**What to observe:**
- The agent may call multiple tools in sequence
- Each step shows: thought → tool name → input → output
- Maximum 5 steps to prevent infinite loops

---

### Tab 5: Fine-Tune

**Concept:** Specialize a base model using small LoRA adapter weights.

**How to use:**
1. Install `fine_tuning/requirements.txt`
2. Preview the instruction dataset
3. Train the LoRA adapter
4. Generate with the adapter
5. Compare base and fine-tuned outputs

Training is intentionally small and educational. For complete instructions, see
[`fine_tuning/docs/RUN_AND_USE.md`](../fine_tuning/docs/RUN_AND_USE.md).

---

### Tab 6: Concepts

**Concept:** Quick reference for every AI concept in the project.

**Contents:**
- What each concept means
- Which source file implements it
- How to try it in the app
- ASCII architecture diagram

Use this tab as a map while reading the code.

---

## 6. Command-Line Tools

### Ingest Documents

```bash
python scripts/ingest.py
```

Reads all `.txt` and `.md` files from `data/sample_docs/`, chunks them, creates embeddings, and stores them in ChromaDB.

**Output example:**
```
Ingesting documents from: .../data/sample_docs
  01_generative_ai.txt: 3 chunks
  02_rag.txt: 4 chunks
  ...
Done! Total files: 4
```

### Add Your Own Documents

1. Place `.txt` or `.md` files in `data/sample_docs/`
2. Run `python scripts/ingest.py` again
3. Ask questions about your new content in the RAG tab

### Compile the Open Wiki

```bash
python scripts/compile_wiki.py
```

This call follows:

```text
data/sample_docs/* → compile_directory() → compile_file()
→ LLM or demo compiler → data/wiki/pages/*.md → refreshed index.md
```

To compile a different directory from Python:

```python
from pathlib import Path
from src.wiki.pipeline import compile_directory

result = compile_directory(Path("my_documents"))
print(result)
```

To query without the web UI:

```python
from src.wiki.pipeline import wiki_query

result = wiki_query("How does RAG differ from Open Wiki?", top_k=3)
print(result["answer"])
for page in result["pages"]:
    print(page["slug"], page["score"])
```

---

## 7. MCP Server Setup

MCP (Model Context Protocol) lets external AI apps use this project's tools.

### Start the Server

```bash
python -m src.mcp.server
```

### Connect from Cursor

Add to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "ai-learning-lab": {
      "command": "python",
      "args": ["-m", "src.mcp.server"],
      "cwd": "C:/Users/nila0425/Downloads/AI_APP"
    }
  }
}
```

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `calc` | Evaluate math expressions |
| `weather` | Get weather for a city |
| `current_time` | Get current date/time |
| `rag_search` | Search document chunks through RAG |
| `wiki_search` | Search compiled Open Wiki pages |

**Example MCP requests from a connected client:**
- `rag_search(query="What is RAG?")`
- `wiki_search(query="What is Open Wiki?")`

The MCP server must run with the project root as its working directory so imports
and `.env` resolution work correctly.

---

## 8. Learning Exercises

Work through these in order to build understanding:

### Exercise 1: Chat Memory
1. Open Chat tab
2. Say "My favorite color is blue"
3. Ask "What's my favorite color?"
4. **Goal:** Understand how conversation history works

### Exercise 2: RAG Retrieval
1. Open RAG tab → Ingest Sample Docs
2. Ask "What is the ReAct pattern?"
3. Expand retrieved chunks
4. **Goal:** See how semantic search finds relevant text

### Exercise 3: Agent Tool Selection
1. Open Agent tab
2. Ask "What is 100 / 4 + sqrt(81)?"
3. Expand reasoning steps
4. **Goal:** Watch the agent choose the calculator tool

### Exercise 4: RAG vs Open Wiki
1. Ask "What is RAG?" in the RAG tab
2. Ask the same question in the Open Wiki tab
3. Compare retrieved chunks with matched wiki pages
4. Open `data/wiki/pages/concepts/open-wiki.md`
5. **Goal:** Understand vector retrieval versus compiled knowledge

### Exercise 5: Multi-Tool Agent
1. Ask "What's 15*23 and the weather in Tokyo?"
2. **Goal:** See the agent call multiple tools in sequence

### Exercise 6: Read the Code
1. Open `src/chat/service.py` — chat logic
2. Open `src/rag/pipeline.py` — RAG pipeline
3. Open `src/wiki/pipeline.py` and `src/wiki/store.py` — Open Wiki
4. Open `src/agents/agent.py` — agent loop
5. **Goal:** Connect UI behavior to source code

### Exercise 7: Modify a System Prompt
1. Edit the `system_prompt` in `src/chat/service.py`
2. Restart the app
3. Ask the same question — notice different behavior
4. **Goal:** Learn prompt engineering hands-on

---

## 9. Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `ModuleNotFoundError` | Virtual env not active or deps missing | Activate `.venv`, run `pip install -r requirements.txt` |
| Ollama connection error | Ollama not running | Start Ollama app or run `ollama serve` |
| `model not found` | Model not downloaded | Run `ollama pull llama3.2` |
| Slow first RAG query | Embedding model downloading | Wait ~1–2 minutes on first run |
| Empty RAG answers | No documents indexed | Click "Ingest Sample Docs" or run `scripts/ingest.py` |
| No wiki pages found | Wiki pages missing or path incorrect | Run `python scripts/compile_wiki.py` and check `data/wiki/pages/` |
| Duplicate wiki topics | Curated and generated slugs both exist | Remove unwanted generated pages or standardize source filenames/slugs |
| Wiki answer shows source pages only | Demo mode is active | Use Ollama/OpenAI for generated synthesis |
| Port 8501 in use | Another Streamlit app running | Use `python -m streamlit run app.py --server.port 8502` |
| Demo mode responses only | `LLM_PROVIDER=demo` in `.env` | Switch to `ollama` or `openai` |
| OpenAI auth error | Invalid or missing API key | Check `OPENAI_API_KEY` in `.env` |

---

## 10. FAQ

**Q: Do I need an API key?**
No. Use demo mode or Ollama (free, local).

**Q: Can I use this offline?**
Yes, with demo mode or Ollama. RAG embeddings also run locally. Only OpenAI requires internet.

**Q: Where is my data stored?**
Vector embeddings are in `data/chroma_db/`. Open Wiki pages are in
`data/wiki/pages/`. Chat history is in memory only (not persisted).

**Q: How do I add more tools to the agent?**
Add a function in `src/agents/tools.py`, register it in `TOOLS` and `TOOL_SCHEMAS`.

**Q: What's the difference between RAG and the Agent's search_knowledge tool?**
They use the same RAG pipeline. The RAG tab is a direct UI; the agent calls it as a tool when it decides search is needed.

**Q: What's the difference between Open Wiki and the Agent's search_wiki tool?**
They use the same `wiki_query()` pipeline. The Open Wiki tab calls it directly;
the agent can select `search_wiki` as a tool.

**Q: Can Open Wiki run without embeddings or ChromaDB?**
Yes. Wiki page search is keyword-based and reads markdown files directly.
Compilation and generated answers use the configured LLM; demo mode provides a
basic local compilation and displays matched pages.

---

## Related Documentation

- [Demo Accuracy Guide](DEMO_PROJECT_GUIDE.md) — what is complete, simplified, or mock
- [Architecture Guide](ARCHITECTURE_GUIDE.md) — system design and components
- [Call Flow Guide](CALL_FLOW_GUIDE.md) — step-by-step request flows
- [Concepts Guide](CONCEPTS.md) — AI concept explanations
- [Getting Started](GETTING_STARTED.md) — quick setup checklist
