# Medical Assistant — User Guide

Learn healthcare AI by using the Medical Assistant application.

> ⚠️ Educational only — not for real medical decisions.

---

## What This Teaches

Building the same AI architecture as the main lab, but for **healthcare**:

1. **Healthcare chatbots** — safe patient education conversations
2. **Medical RAG** — search clinical/education documents
3. **Medical agents** — BMI, symptoms, medications, specialist lookup
4. **Medical MCP** — connect AI to hospital tools
5. **Safety** — disclaimers, no diagnosis, regulatory awareness

---

## Installation & Run

See [RUN_AND_USE.md](RUN_AND_USE.md) for full instructions.

```bash
pip install -r requirements.txt
python -m streamlit run medical_assistant/app.py
```

---

## Feature Guide

### Medical Chat
- **Purpose:** Learn healthcare conversational AI
- **Safety:** System prompt forbids diagnosis and prescribing
- **Try:** "Explain the circulatory system" / "What is a normal heart rate?"

### Medical RAG
- **Purpose:** Ground answers in health education documents
- **Must do first:** Ingest medical docs
- **Try:** "What is the DRSABC first aid survey?" / "What foods are in a balanced diet?"

### Medical Agent
- **Purpose:** AI that uses medical tools autonomously
- **Tools:** BMI, symptoms, drugs, specialists, KB search
- **Try:** Multi-step: "Calculate my BMI (75kg, 1.68m) and find a dermatologist"

### Learn Tab
- Concept map and integration diagram

---

## Learning Exercises

### Exercise 1: Chat Safety
Ask: "Diagnose my headache" — observe how the tutor refuses and redirects to a doctor.

### Exercise 2: RAG Grounding
Ingest docs → ask "What is hypertension?" → verify answer cites `02_common_conditions.txt`.

### Exercise 3: Agent Tool Selection
Ask agent to calculate BMI — watch `bmi_calculator` tool in reasoning steps.

### Exercise 4: Agent + RAG Integration
Ask: "Search medical KB for CPR steps" — agent calls `search_medical_kb` which uses RAG.

### Exercise 5: Compare Domains
Run the same question in **main app** (general) vs **medical app** — see how domain changes prompts, tools, and documents.

### Exercise 6: Read the Code
- `chat/service.py` — medical system prompt
- `agents/tools.py` — mock medical databases
- `rag/pipeline.py` — separate medical vector store

---

## Healthcare AI in Production

This project demonstrates architecture. Real healthcare AI requires:

| Requirement | This Project | Production |
|-------------|-------------|------------|
| Accuracy | Educational mock data | Clinically validated data |
| Safety | Text disclaimers | Regulatory approval (FDA, CE) |
| Privacy | Local only | HIPAA, GDPR compliance |
| Liability | None (learning) | Medical malpractice insurance |
| Human oversight | None | Clinician-in-the-loop |

---

## Related Docs

- [Run and Use](RUN_AND_USE.md)
- [Architecture](ARCHITECTURE.md)
- [Integration Diagram](INTEGRATION_DIAGRAM.md)
- [Main AI Lab](../../docs/RUN_AND_USE.md)
