# Getting Started Guide

This guide walks you through setting up and running the AI Learning Lab step by step.

## Step 1: Install Python

You need Python 3.10 or higher. Check your version:

```bash
python --version
```

If you don't have Python, download it from [python.org](https://www.python.org/downloads/).

## Step 2: Create a Virtual Environment

A virtual environment keeps project dependencies isolated:

```bash
cd AI_APP
python -m venv .venv
```

Activate it:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Streamlit, ChromaDB, sentence-transformers, MCP, and other packages.
The first run will download the embedding model (~80 MB).

## Step 4: Choose Your LLM Provider

Copy the example config:

```bash
copy .env.example .env
```

### Option A: Ollama (Recommended — Free & Local)

1. Download and install [Ollama](https://ollama.com)
2. Pull a model:
   ```bash
   ollama pull llama3.2
   ```
3. Edit `.env`:
   ```
   LLM_PROVIDER=ollama
   OLLAMA_MODEL=llama3.2
   ```

### Option B: OpenAI (Requires API Key)

1. Get an API key from [platform.openai.com](https://platform.openai.com)
2. Edit `.env`:
   ```
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-your-actual-key
   OPENAI_MODEL=gpt-4o-mini
   ```

### Option C: Demo Mode (No LLM Needed)

If you just want to explore the UI and code without an LLM:

```
LLM_PROVIDER=demo
```

Demo mode uses rule-based responses so you can see how the app flows work.

## Step 5: Run the App

```bash
python -m streamlit run app.py
```

Your browser opens at **http://localhost:8501**.

## Step 6: Try Each Feature

### Chat Tab
Type a message and press Enter. The LLM responds with conversation memory.

### RAG Tab
1. Click **"Ingest Sample Docs"** to load learning documents
2. Ask a question like "What is RAG?" or "How do embeddings work?"
3. See the retrieved chunks and generated answer

### Agent Tab
Try these example queries:
- "What is 25 * 17?" (uses calculator tool)
- "What's the weather in London?" (uses weather tool)
- "What time is it?" (uses time tool)
- "Search the docs: what is an AI agent?" (uses RAG tool)

Watch the reasoning steps to see the agent decide which tool to use.

### Fine-Tune Tab
Install `fine_tuning/requirements.txt`, then preview the dataset, train a LoRA
adapter, run inference, and compare base versus fine-tuned outputs.

### Concepts Tab
Read about each AI concept and where to find it in the code.

## Step 7: Load Documents (Optional)

Pre-load sample documents from the command line:

```bash
python scripts/ingest.py
```

## Step 8: Run the MCP Server (Optional)

The MCP server exposes tools to external AI clients like Cursor:

```bash
python -m src.mcp.server
```

To connect from Cursor, add to your MCP config:

```json
{
  "mcpServers": {
    "ai-learning-lab": {
      "command": "python",
      "args": ["-m", "src.mcp.server"],
      "cwd": "C:/path/to/AI_APP"
    }
  }
}
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Make sure virtual env is activated and deps are installed |
| Ollama connection error | Run `ollama serve` or restart Ollama app |
| Slow first RAG query | Embedding model downloads on first use (~80 MB) |
| Empty RAG answers | Click "Ingest Sample Docs" first |
| Port 8501 in use | Run `python -m streamlit run app.py --server.port 8502` |

## Verify Everything Works

```bash
python scripts/smoke_test.py
python scripts/ui_smoke_test.py
```

If both pass, the core app, Open Wiki tab, Agent tools, and MCP registration are working.

## Next Steps

- Read [DEMO_PROJECT_GUIDE.md](DEMO_PROJECT_GUIDE.md) first — what is real vs simplified in this demo
- Read [RUN_AND_USE.md](RUN_AND_USE.md) for complete install, run, and use instructions
- Read [INTEGRATION_DIAGRAM.md](INTEGRATION_DIAGRAM.md) to see how everything connects
- Read [USER_GUIDE.md](USER_GUIDE.md) for a complete walkthrough
- Read [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) for system design
- Read [CALL_FLOW_GUIDE.md](CALL_FLOW_GUIDE.md) for step-by-step request flows
- Read [CONCEPTS.md](CONCEPTS.md) for detailed AI explanations
- Modify the code — change system prompts, add new tools, try different models
- Add your own documents to `data/sample_docs/` and re-ingest
