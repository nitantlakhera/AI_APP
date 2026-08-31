# How to Run and Use — Complete Guide

Step-by-step instructions to **install**, **run**, and **use** every part of the AI Learning Lab.

> **Visual learning guides:** Open [docs/html/index.html](html/index.html) in your browser for step-by-step HTML flow pages and **PNG architecture diagrams** (LLM architecture, pipeline structure, system integration).
>
> **Accuracy guide:** Read [what is real and what is simplified](DEMO_PROJECT_GUIDE.md)
> before interpreting demo-mode results.

---

## Table of Contents

1. [First-Time Setup (5 Minutes)](#1-first-time-setup-5-minutes)
2. [Run the Main Application](#2-run-the-main-application)
3. [How to Use Each Feature](#3-how-to-use-each-feature)
4. [Run Fine-Tuning Module](#4-run-fine-tuning-module)
5. [Run MCP Server](#5-run-mcp-server)
6. [All Commands Cheat Sheet](#6-all-commands-cheat-sheet)
7. [Complete First Session Walkthrough](#7-complete-first-session-walkthrough)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. First-Time Setup (5 Minutes)

### Step 1: Open terminal in project folder

```bash
cd C:\Users\nila0425\Downloads\AI_APP
```

### Step 2: Create and activate virtual environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Windows Command Prompt)
.venv\Scripts\activate.bat
```

You should see `(.venv)` in your terminal.

### Step 3: Install dependencies

```bash
# Main app
pip install -r requirements.txt

# Fine-tuning module (optional — install when you need it)
pip install -r fine_tuning/requirements.txt
```

### Step 4: Create config file

```bash
copy .env.example .env
```

### Step 5: Choose LLM mode (edit `.env`)

**Easiest — Demo mode (no API key, works immediately):**
```env
LLM_PROVIDER=demo
```

**Best for learning — Ollama (free local AI):**
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
```
Then install [Ollama](https://ollama.com) and run: `ollama pull llama3.2`

**Cloud AI — OpenAI:**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

---

## 2. Run the Main Application

### Start the web app

```bash
python -m streamlit run app.py
```

**Browser opens at:** http://localhost:8501

If port 8501 is busy:
```bash
python -m streamlit run app.py --server.port 8502
```

### Stop the app

Press `Ctrl + C` in the terminal.

### Pre-load RAG documents (optional but recommended)

Open a **second terminal** (keep the app running):

```bash
cd C:\Users\nila0425\Downloads\AI_APP
.venv\Scripts\Activate.ps1
python scripts/ingest.py
```

This indexes sample learning documents into the vector database.

---

## 3. How to Use Each Feature

### Sidebar (left panel)

When the app loads, check the sidebar:
- **LLM Status** — connected, demo mode, or configured-provider error
- **Docs indexed** — number of RAG chunks loaded (0 until you ingest)
- **Learning Guides** — paths and commands for opening project documentation

---

### Tab 1: Chat — Talk to the AI

**What it teaches:** Generative AI, conversation memory

**How to use:**
1. Click the **Chat** tab
2. Type a message in the box at the bottom
3. Press **Enter**
4. Read the reply

**Try these:**
```
Hello, my name is Alex.
What is my name?
Explain generative AI in simple terms.
```

**Tips:**
- The AI remembers earlier messages in the same session
- Click **Clear Chat** to start fresh
- Edit system prompt in `src/chat/service.py` to change behavior

---

### Tab 2: RAG — Ask Questions About Documents

**What it teaches:** Retrieval Augmented Generation

**How to use:**
1. Click the **RAG** tab
2. Click **"Ingest Sample Docs"** (left side) — wait a few seconds
3. Type a question, e.g. `What is RAG?`
4. Click **"Search & Answer"**
5. Read the answer
6. Expand **Retrieved Chunks** to see which document parts were used

**Try these questions:**
| Question | Expected source |
|----------|----------------|
| What is generative AI? | 01_generative_ai.txt |
| What is RAG? | 02_rag.txt |
| How do AI agents work? | 03_agents.txt |
| What are embeddings? | 04_embeddings.txt |

**Tips:**
- You must ingest docs first — otherwise answers will be empty
- In demo mode, you see retrieved chunks directly
- With Ollama/OpenAI, the LLM generates an answer from those chunks

---

### Tab 3: Open Wiki — Persistent Knowledge Base (Alternative to RAG)

**What it teaches:** The LLM Wiki pattern — compiled markdown knowledge instead of vector retrieval

**How to use:**
1. Click the **Open Wiki** tab
2. Browse pre-built pages in the expander (or click **Compile Sample Docs** to rebuild from raw files)
3. Type a question, e.g. `What is the difference between RAG and Open Wiki?`
4. Click **Query Wiki**
5. Compare the same question in the **RAG** tab — notice RAG returns raw chunks, Wiki returns synthesized pages

**Try these questions:**
| Question | Expected wiki page |
|----------|-------------------|
| What is generative AI? | concepts/generative-ai |
| What is RAG? | concepts/rag |
| How do AI agents work? | concepts/agents |
| What is Open Wiki vs RAG? | concepts/open-wiki |

**CLI compile:** `python scripts/compile_wiki.py`

**Tips:**
- Wiki pages live in `data/wiki/pages/` — open them in any text editor
- No embeddings or vector DB needed for wiki search
- Pre-built pages work immediately; compile refreshes them from sample docs

---

### Tab 4: Agent — AI That Uses Tools

**What it teaches:** Agentic AI, tool calling, ReAct loop

**How to use:**
1. Click the **Agent** tab
2. Type a task OR click an example button
3. Click **"Run Agent"**
4. Read the **Final Answer**
5. Expand **Reasoning Steps** to see which tools were called

**Try these tasks:**
| Task | What happens |
|------|-------------|
| `What is 25 * 17?` | Calls calculator tool |
| `What's the weather in London?` | Calls weather tool |
| `What time is it?` | Calls time tool |
| `Search the docs: what is MCP?` | Calls RAG search (ingest docs first!) |
| `Search the wiki: what is Open Wiki?` | Calls Open Wiki search |

**Tips:**
- Agent can call multiple tools in one task
- Each step shows: thought → tool → input → output
- Max 5 steps to prevent infinite loops

---

### Tab 5: Fine-Tune — Specialize a Model with LoRA

**What it teaches:** Parameter-efficient fine-tuning, inference, and evaluation

**How to use:**
1. Install the optional dependencies: `pip install -r fine_tuning/requirements.txt`
2. Open the **Fine-Tune** tab
3. Preview the dataset
4. In **Train**, click **Start LoRA Training**
5. Use **Infer** and **Evaluate** after training completes

---

### Tab 6: Concepts — Learning Reference

**What it teaches:** Map of all AI concepts in the project

**How to use:**
1. Click the **Concepts** tab
2. Expand any concept to read what it is, where in code, and how to try it
3. Scroll down for the **integration diagram** showing how everything connects

---

## 4. Run Fine-Tuning Module

Fine-tuning is available in the main app’s **Fine-Tune** tab and as a standalone app.

### Setup (one time)

```bash
pip install -r fine_tuning/requirements.txt
copy fine_tuning\.env.example fine_tuning\.env
```

### Option A: Web UI

```bash
python -m streamlit run fine_tuning/app.py
```

Open http://localhost:8501 (stop main app first if port is in use, or use port 8502).

**Tabs:**
| Tab | What to do |
|-----|-----------|
| **Dataset** | Preview training examples |
| **Train** | Click "Start Training" — takes 5–15 min on CPU |
| **Infer** | Type instruction, click Generate |
| **Evaluate** | Compare base vs fine-tuned model |

### Option B: Command Line

```bash
# Train LoRA adapter (~5-15 min on CPU)
python fine_tuning/scripts/train.py

# Compare base vs fine-tuned
python fine_tuning/scripts/evaluate.py

# Generate text
python fine_tuning/scripts/infer.py "What is LoRA?"
```

---

## 5. Run MCP Server

MCP lets external apps (Cursor, Claude Desktop) use this project's tools.

### Start the server

```bash
python -m src.mcp.server
```

The server runs via stdio — it waits for an MCP client to connect.

### Connect from Cursor

Add to your Cursor MCP settings (`settings.json` or MCP config):

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

### Available MCP tools

| Tool | Example use |
|------|-------------|
| `calc` | `2 + 2 * 10` |
| `weather` | `London` |
| `current_time` | (no input) |
| `rag_search` | `What is RAG?` (ingest docs first) |
| `wiki_search` | `What is Open Wiki?` |

---

## 6. All Commands Cheat Sheet

### Main App

| Action | Command |
|--------|---------|
| Install | `pip install -r requirements.txt` |
| Configure | `copy .env.example .env` |
| **Run app** | `python -m streamlit run app.py` |
| Ingest docs | `python scripts/ingest.py` |
| Compile Open Wiki | `python scripts/compile_wiki.py` |
| Core functional checks | `python scripts/smoke_test.py` |
| All Streamlit UI checks | `python scripts/ui_smoke_test.py` |
| Run MCP server | `python -m src.mcp.server` |

### Fine-Tuning Module

| Action | Command |
|--------|---------|
| Install | `pip install -r fine_tuning/requirements.txt` |
| Configure | `copy fine_tuning\.env.example fine_tuning\.env` |
| **Run UI** | `python -m streamlit run fine_tuning/app.py` |
| Train | `python fine_tuning/scripts/train.py` |
| Evaluate | `python fine_tuning/scripts/evaluate.py` |
| Infer | `python fine_tuning/scripts/infer.py "Your question"` |

### Environment Activation (every new terminal)

```bash
cd C:\Users\nila0425\Downloads\AI_APP
.venv\Scripts\Activate.ps1
```

---

## 7. Complete First Session Walkthrough

Follow this exactly on your first run (~15 minutes):

### Minute 0–5: Setup

```bash
cd C:\Users\nila0425\Downloads\AI_APP
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` — set `LLM_PROVIDER=demo` (works without any API key).

### Minute 5–7: Start app

```bash
python -m streamlit run app.py
```

Browser opens → you see 6 tabs: Chat, RAG, Open Wiki, Agent, Fine-Tune, and Concepts.

### Minute 7–9: Try Chat

1. Go to **Chat** tab
2. Type: `Hello! What can you teach me?`
3. Press Enter
4. Read the response

### Minute 9–12: Try RAG

1. Go to **RAG** tab
2. Click **"Ingest Sample Docs"**
3. Wait for success message
4. Type: `What is an AI agent?`
5. Click **"Search & Answer"**
6. Expand retrieved chunks

### Minute 12–15: Try Agent

1. Go to **Agent** tab
2. Click example: `What is 15 * 23 + sqrt(144)?`
3. Click **"Run Agent"**
4. Expand reasoning steps — see calculator tool being called

### Done!

You have used the three core runtime features. Next, explore **Fine-Tune** and **Concepts**, then:
- Read [CONCEPTS.md](CONCEPTS.md) to understand what you just did
- Read [INTEGRATION_DIAGRAM.md](INTEGRATION_DIAGRAM.md) to see how they connect
- Switch to Ollama for real AI responses

---

## 8. Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Activate `.venv` and run `pip install -r requirements.txt` |
| `streamlit: command not found` | Use `python -m streamlit run app.py` |
| App won't open in browser | Manually go to http://localhost:8501 |
| Port 8501 in use | `python -m streamlit run app.py --server.port 8502` |
| Demo mode only | Set `LLM_PROVIDER=ollama` or `openai` in `.env` |
| Ollama connection error | Start Ollama app, run `ollama pull llama3.2` |
| Empty RAG answers | Click "Ingest Sample Docs" or run `python scripts/ingest.py` |
| Slow first RAG query | Embedding model downloading (~80 MB) — wait once |
| Agent search returns nothing | Ingest docs first (RAG tab or `scripts/ingest.py`) |
| Fine-tuning out of memory | Set `BATCH_SIZE=1` in `fine_tuning/.env` |
| PowerShell won't activate venv | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│  AI LEARNING LAB — QUICK START                          │
├─────────────────────────────────────────────────────────┤
│  1. cd AI_APP                                           │
│  2. .venv\Scripts\Activate.ps1                          │
│  3. pip install -r requirements.txt                     │
│  4. copy .env.example .env                              │
│  5. python -m streamlit run app.py                      │
│  6. Open http://localhost:8501                          │
├─────────────────────────────────────────────────────────┤
│  TABS: Chat | RAG | Agent | Fine-Tune | Concepts        │
│  FIRST: Ingest docs in RAG tab before using RAG/Agent   │
├─────────────────────────────────────────────────────────┤
│  FINE-TUNING: python -m streamlit run fine_tuning/app.py│
│  MCP SERVER:  python -m src.mcp.server                  │
└─────────────────────────────────────────────────────────┘
```

---

## Related Documentation

- **[HTML Learning Flows](html/index.html)** — visual step-by-step guides (open in browser)
- [User Guide](USER_GUIDE.md) — detailed feature guide
- [Getting Started](GETTING_STARTED.md) — setup checklist
- [Concepts](CONCEPTS.md) — what each AI concept means
- [Integration Diagram](INTEGRATION_DIAGRAM.md) — how components connect
- [Advanced Concepts](ADVANCED_CONCEPTS.md) — expert roadmap
- [Medical Assistant](../medical_assistant/README.md) — healthcare domain app
- [Fine-Tuning Lab](../fine_tuning/README.md) — LoRA training module
