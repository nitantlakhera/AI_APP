# Medical Assistant — How to Run and Use

Complete guide to install, run, and use the Medical Assistant Learning Lab.

> ⚠️ **Educational project only — not for real medical use.**

---

## 1. Setup

```bash
cd C:\Users\nila0425\Downloads\AI_APP

# Use main project dependencies (if not already installed)
pip install -r requirements.txt

# Configure LLM (root .env is shared)
copy .env.example .env
# Set: LLM_PROVIDER=demo  (or ollama / openai)
```

## 2. Run the App

```bash
python -m streamlit run medical_assistant/app.py
```

Open **http://localhost:8501**

## 3. Pre-load Medical Documents

```bash
python medical_assistant/scripts/ingest.py
```

Or click **"Ingest Medical Docs"** in the RAG tab.

## 4. How to Use Each Tab

### Medical Chat
1. Type a health education question
2. Press Enter
3. Get an educational response (with safety disclaimers)

**Try:** `What are the main body systems?` or `Explain hypertension in simple terms`

### Medical RAG
1. Click **Ingest Medical Docs**
2. Ask: `What is CPR?` or `What are the signs of diabetes?`
3. View answer + retrieved document chunks

### Medical Agent
1. Click an example or type a task
2. Click **Run Medical Agent**
3. Expand reasoning steps to see tools used

**Try:**
| Task | Tool used |
|------|-----------|
| BMI for 70kg, 1.75m | `bmi_calculator` |
| Info about fever | `symptom_lookup` |
| What is paracetamol? | `medication_info` |
| Find cardiologist | `find_specialist` |
| Search: first aid for burns | `search_medical_kb` |

### Learn Tab
- Concept map and integration diagram

## 5. Run MCP Server

```bash
python -m medical_assistant.src.mcp.server
```

Cursor MCP config:
```json
{
  "mcpServers": {
    "medical-assistant": {
      "command": "python",
      "args": ["-m", "medical_assistant.src.mcp.server"],
      "cwd": "C:/Users/nila0425/Downloads/AI_APP"
    }
  }
}
```

## 6. Commands Cheat Sheet

| Action | Command |
|--------|---------|
| Run app | `python -m streamlit run medical_assistant/app.py` |
| Ingest docs | `python medical_assistant/scripts/ingest.py` |
| MCP server | `python -m medical_assistant.src.mcp.server` |

## 7. First Session (10 min)

1. Start app
2. **Chat:** Ask about body systems
3. **RAG:** Ingest docs → ask about first aid
4. **Agent:** Calculate BMI for 65kg, 1.70m
5. Read **Learn** tab integration diagram

## 8. Troubleshooting

| Problem | Solution |
|---------|----------|
| Empty RAG answers | Ingest medical docs first |
| Demo mode only | Set `LLM_PROVIDER=ollama` in root `.env` |
| Import errors | Run from `AI_APP` root, install `requirements.txt` |

---

See also: [Architecture](ARCHITECTURE.md) | [Integration Diagram](INTEGRATION_DIAGRAM.md)
