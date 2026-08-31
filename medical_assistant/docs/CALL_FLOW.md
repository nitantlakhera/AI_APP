# Medical Assistant — Call Flow Guide

Step-by-step flows for every operation.

---

## Chat Flow

```
User types "What is hypertension?"
  → MedicalChatSession.send()
  → messages + medical system prompt (safety rules)
  → llm_bridge → src/llm/provider.py
  → response with educational disclaimer
  → display in UI
```

## RAG Ingest Flow

```
Click "Ingest Medical Docs"
  → ingest_directory(medical_assistant/data/sample_docs/)
  → For each .txt: chunk → embed → Medical ChromaDB
  → 5 files indexed (separate from main app ChromaDB)
```

## RAG Query Flow

```
User asks "What is CPR?"
  → medical_rag_query()
  → embed query → search Medical ChromaDB
  → retrieve chunks from 03_first_aid_basics.txt
  → build prompt with medical context + safety rules
  → LLM generates answer + disclaimer
  → show answer + source chunks
```

## Agent Flow — BMI Example

```
User: "Calculate BMI for 70kg and 1.75m"
  → MedicalAgent.run()
  → LLM → tool_call: bmi_calculator(70, 1.75)
  → result: "BMI: 22.9 (normal weight)..."
  → LLM → final answer with disclaimer
```

## Agent Flow — RAG Tool

```
User: "Search medical KB for diabetes symptoms"
  → Agent → search_medical_kb("diabetes symptoms")
  → medical_rag_query()  ← SAME as RAG tab
  → returns grounded answer from 02_common_conditions.txt
  → Agent presents to user
```

## MCP Flow

```
Cursor → tools/call {name: "medical_search", query: "first aid burns"}
  → mcp/server.py → medical_rag_query()
  → JSON result returned to client
```

---

## Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant UI as medical_assistant/app.py
    participant Agent as MedicalAgent
    participant Tools as agents/tools.py
    participant RAG as medical_rag_query
    participant LLM as src/llm/provider

    User->>UI: "BMI 70kg 1.75m + search diabetes"
    UI->>Agent: run(query)
    Agent->>LLM: chat + tool schemas
    LLM-->>Agent: bmi_calculator tool call
    Agent->>Tools: bmi_calculator(70, 1.75)
    Tools-->>Agent: BMI result
    Agent->>LLM: tool result
    LLM-->>Agent: search_medical_kb tool call
    Agent->>Tools: search_medical_kb("diabetes")
    Tools->>RAG: medical_rag_query()
    RAG->>LLM: generate with context
    LLM-->>RAG: answer
    RAG-->>Tools: RAG result
    Tools-->>Agent: KB answer
    Agent->>LLM: synthesize
    LLM-->>Agent: final answer
    Agent-->>UI: AgentResult
    UI-->>User: display
```

---

## File Map

| Action | Entry | Core Logic |
|--------|-------|------------|
| Chat | app.py Chat tab | `chat/service.py` |
| RAG ingest | app.py / scripts/ingest.py | `rag/pipeline.py` |
| RAG query | app.py RAG tab | `rag/pipeline.py` |
| Agent | app.py Agent tab | `agents/agent.py` |
| MCP | `python -m medical_assistant.src.mcp.server` | `mcp/server.py` |
