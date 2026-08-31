"""Medical Assistant — Streamlit learning application."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st

from medical_assistant import DISCLAIMER
from medical_assistant.src.agents.agent import MedicalAgent
from medical_assistant.src.chat.service import MedicalChatSession
from medical_assistant.src.config import settings
from medical_assistant.src.llm_bridge import llm
from medical_assistant.src.rag.pipeline import ingest_directory, medical_rag_query, vector_store

st.set_page_config(
    page_title="Medical Assistant Lab",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.warning(DISCLAIMER)

with st.sidebar:
    st.title("🏥 Medical Assistant Lab")
    st.caption("Learn healthcare AI — Chat, RAG, Agents, MCP")
    st.divider()

    st.subheader("LLM Status")
    status = llm.check_connection()
    if llm.is_demo_mode:
        st.info("Demo mode — no external LLM required")
    elif status["status"] == "ok":
        if status.get("verified") is False:
            st.success(f"Configured: {status.get('provider', 'unknown')} (not contacted yet)")
        else:
            st.success(f"Connected: {status.get('provider', 'unknown')}")
    else:
        st.error(f"{llm.provider.title()} is configured but unavailable")
        st.caption(status.get("message", ""))

    st.divider()
    st.caption(f"Medical docs indexed: {vector_store.document_count} chunks")
    st.divider()
    st.markdown("**Learning guides**")
    st.caption("Open `docs/html/medical-assistant-flow.html` for the visual flow.")
    st.code(r"start docs\html\medical-assistant-flow.html", language="powershell")
    st.caption("Detailed guides are in `medical_assistant/docs/`.")

tab_chat, tab_rag, tab_agent, tab_learn = st.tabs([
    "💬 Medical Chat", "📚 Medical RAG", "🤖 Medical Agent", "📖 Learn"
])

# ── Chat ─────────────────────────────────────────────────────────────
with tab_chat:
    st.header("Medical Education Chat")
    st.markdown("Ask health education questions. **Not for real medical advice.**")

    if "med_chat" not in st.session_state:
        st.session_state.med_chat = MedicalChatSession()

    for msg in st.session_state.med_chat.get_history_display():
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Ask a medical education question..."):
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    reply = st.session_state.med_chat.send(prompt)
                except Exception as exc:
                    st.error(f"LLM request failed: {exc}")
                else:
                    st.write(reply)

    if st.button("Clear Chat", key="med_clear"):
        st.session_state.med_chat.clear()
        st.rerun()

# ── RAG ─────────────────────────────────────────────────────────────
with tab_rag:
    st.header("Medical RAG — Search Health Documents")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Load Medical Docs")
        if st.button("Ingest Medical Docs"):
            with st.spinner("Indexing..."):
                results = ingest_directory(Path(settings.sample_docs_dir))
            st.success(f"Indexed: {results}" if results else "No files found")
        st.caption(f"Indexed: **{vector_store.document_count}** chunks")

    with col2:
        st.subheader("2. Ask a Question")
        q = st.text_input("Question", placeholder="What is hypertension?", key="med_rag_q")
        if st.button("Search & Answer", key="med_rag_btn") and q:
            with st.spinner("Searching..."):
                try:
                    result = medical_rag_query(q)
                except Exception as exc:
                    st.error(f"Medical RAG request failed: {exc}")
                    result = None
            if result:
                st.write(result["answer"])
                if result["chunks"]:
                    for i, c in enumerate(result["chunks"], 1):
                        with st.expander(f"Chunk {i} — {c['metadata'].get('source')} ({c['relevance']})"):
                            st.write(c["text"])

# ── Agent ─────────────────────────────────────────────────────────────
with tab_agent:
    st.header("Medical Agent")
    st.markdown("Agent uses medical tools: BMI, symptoms, medications, specialists, KB search.")

    examples = [
        "Calculate BMI for 70kg and 1.75m height",
        "Look up educational info about fever",
        "What is paracetamol used for?",
        "Find a cardiologist in London",
        "Search medical KB: what is CPR?",
    ]
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        if cols[i % 2].button(ex, key=f"med_ex_{i}"):
            st.session_state.med_agent_q = ex

    agent_q = st.text_input("Task", value=st.session_state.get("med_agent_q", ""), key="med_agent_input")
    if st.button("Run Medical Agent") and agent_q:
        with st.spinner("Agent working..."):
            try:
                result = MedicalAgent().run(agent_q)
            except Exception as exc:
                st.error(f"Medical agent request failed: {exc}")
                result = None
        if result:
            st.success(result.answer)
            for step in result.steps:
                with st.expander(f"Step {step.step_number}: {step.thought}"):
                    if step.tool_name:
                        st.json({"tool": step.tool_name, "input": step.tool_input})
                        st.code(step.tool_output or "")

# ── Learn ─────────────────────────────────────────────────────────────
with tab_learn:
    st.header("Medical AI Concepts")
    concepts = {
        "Healthcare Chatbot": ("Patient education Q&A with safety disclaimers", "src/chat/service.py"),
        "Medical RAG": ("Search clinical/education docs for grounded answers", "src/rag/pipeline.py"),
        "Medical Agent": ("BMI, symptoms, drugs, specialists + KB search", "src/agents/"),
        "Medical MCP": ("Connect to hospital systems via standard protocol", "src/mcp/server.py"),
        "Safety & Compliance": ("Disclaimers, no diagnosis, HITL in production", "All modules"),
    }
    for name, (desc, path) in concepts.items():
        with st.expander(f"**{name}**"):
            st.markdown(f"**What:** {desc}")
            st.markdown(f"**Code:** `{path}`")

    st.divider()
    st.subheader("Integration Diagram")
    st.code("""
┌─────────────────────────────────────────────────────────────────────┐
│           MEDICAL ASSISTANT (medical_assistant/app.py)               │
│                                                                      │
│  Medical Chat ──► chat/service ──┐                                  │
│  Medical RAG  ──► rag/pipeline ──┼──► LLM Provider (shared)         │
│  Med Agent    ──► agents/agent ──┘         ▲                        │
│                         │                  │                        │
│                    agents/tools            │                        │
│                         │                  │                        │
│              search_medical_kb ────────────┘ (Agent uses RAG!)      │
│                                                                      │
│  Medical ChromaDB ◄── data/sample_docs/ (5 health education files)   │
│                                                                      │
│  MCP Server ──► calc_bmi, symptoms, medication, specialist, search │
└─────────────────────────────────────────────────────────────────────┘

See: medical_assistant/docs/INTEGRATION_DIAGRAM.md
    """, language="text")
