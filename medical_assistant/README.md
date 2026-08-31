# Medical Assistant Learning Lab

A **domain-specific AI application** for students to learn how Generative AI and Agentic AI apply to **healthcare** — with the same architecture as the main AI Learning Lab.

> ⚠️ **EDUCATIONAL ONLY** — This is NOT a real medical device. Never use for actual medical decisions. Always consult a qualified healthcare professional.

## What You'll Learn

| Concept | Medical Application | Code |
|---------|---------------------|------|
| Healthcare Chatbot | Patient education Q&A with safety rules | `src/chat/` |
| Medical RAG | Search health education documents | `src/rag/` |
| Medical Agent | BMI, symptoms, drugs, specialists | `src/agents/` |
| Medical MCP | Connect AI to healthcare tools | `src/mcp/` |
| Safety & Disclaimers | Required in all healthcare AI | All modules |

## Quick Start

```bash
# From project root (uses main app dependencies)
cd C:\Users\nila0425\Downloads\AI_APP
pip install -r requirements.txt
copy .env.example .env   # set LLM_PROVIDER=demo

# Run Medical Assistant
python -m streamlit run medical_assistant/app.py

# Ingest medical docs
python medical_assistant/scripts/ingest.py
```

Open **http://localhost:8501**

## Architecture

Same pattern as main AI Learning Lab, applied to healthcare:

```
Medical Chat ──► LLM
Medical RAG  ──► ChromaDB + LLM
Medical Agent ──► Tools + search_medical_kb ──► RAG
MCP Server   ──► Same medical tools externally
```

See [docs/INTEGRATION_DIAGRAM.md](docs/INTEGRATION_DIAGRAM.md).

## Medical Agent Tools

| Tool | Purpose |
|------|---------|
| `bmi_calculator` | Calculate BMI (educational) |
| `symptom_lookup` | Mock symptom education database |
| `medication_info` | Mock drug information database |
| `find_specialist` | Mock specialist finder |
| `search_medical_kb` | RAG search over health docs |

## Sample Documents

5 educational files in `data/sample_docs/`:
- Human body basics
- Common conditions
- First aid basics
- Nutrition & health
- Medical terminology

## Documentation

- [How to Run and Use](docs/RUN_AND_USE.md)
- [User Guide](docs/USER_GUIDE.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Integration Diagram](docs/INTEGRATION_DIAGRAM.md)
- [Call Flow Guide](docs/CALL_FLOW.md)

## Relation to Main Project

| | Main AI Learning Lab | Medical Assistant |
|---|---------------------|-------------------|
| Domain | General AI education | Healthcare education |
| LLM | Shared (`src/llm/`) | Reuses main LLM provider |
| Vector DB | `data/chroma_db/` | `medical_assistant/data/chroma_db/` |
| Tools | calculator, weather | BMI, symptoms, drugs |
| Architecture | Same | Same pattern, domain-specific |

Students learn: **same AI patterns, different domain application.**
