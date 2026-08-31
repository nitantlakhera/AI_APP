"""Streamlit web UI for the AI Learning Lab."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on the path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.agents.agent import Agent
from src.chat.service import ChatSession
from src.config import settings
from src.llm.provider import llm
from src.rag.pipeline import ingest_directory, rag_query
from src.rag.vectorstore import vector_store
from src.wiki.pipeline import compile_sample_docs, wiki_query
from src.wiki.store import list_pages, wiki_store

st.set_page_config(
    page_title="AI Learning Lab",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🧠 AI Learning Lab")
    st.caption("Learn Generative AI & Agentic AI")
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
        if status.get("configured_model"):
            st.info(f"Model: {status['configured_model']}")
    else:
        st.error(f"{settings.llm_provider.title()} is configured but unavailable")
        st.caption(status.get("message", ""))

    st.divider()
    st.subheader("Learning Guides")
    st.caption("Open `docs/html/index.html` for learning flows + PNG architecture diagrams.")
    st.code(r"start docs\html\index.html", language="powershell")
    st.caption("Diagrams: `docs/images/llm-architecture.png`, `pipeline-structure.png`")

    st.divider()
    st.caption(f"Provider: `{settings.llm_provider}`")
    st.caption(f"Docs indexed: {vector_store.document_count} chunks")
    st.caption(f"Wiki pages: {wiki_store.page_count}")

# ── Main Tabs ────────────────────────────────────────────────────────
tab_chat, tab_rag, tab_wiki, tab_agent, tab_finetune, tab_concepts = st.tabs([
    "💬 Chat",
    "📚 RAG",
    "📖 Open Wiki",
    "🤖 Agent",
    "🎯 Fine-Tune",
    "📖 Concepts",
])

# ── TAB 1: Chat ───────────────────────────────────────────────────────
with tab_chat:
    st.header("Chat Application")
    st.markdown(
        "**Concept:** A multi-turn conversation where the LLM remembers context. "
        "Each message includes the full history so the model can reference earlier turns."
    )

    if "chat_session" not in st.session_state:
        st.session_state.chat_session = ChatSession()

    for msg in st.session_state.chat_session.get_history_display():
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Ask me anything..."):
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    reply = st.session_state.chat_session.send(prompt)
                except Exception as exc:
                    st.error(f"LLM request failed: {exc}")
                else:
                    st.write(reply)

    if st.button("Clear Chat", key="clear_chat"):
        st.session_state.chat_session.clear()
        st.rerun()

# ── TAB 2: RAG ───────────────────────────────────────────────────────
with tab_rag:
    st.header("RAG — Retrieval Augmented Generation")
    st.markdown(
        "**Concept:** Instead of relying only on the LLM's training data, "
        "RAG retrieves relevant documents and includes them in the prompt. "
        "This grounds answers in your own data."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Load Documents")
        if st.button("Ingest Sample Docs"):
            with st.spinner("Indexing documents..."):
                docs_dir = Path(settings.sample_docs_dir)
                results = ingest_directory(docs_dir)
            if results:
                st.success(f"Indexed: {results}")
            else:
                st.warning("No .txt or .md files found in data/sample_docs/")
        st.caption(f"Currently indexed: **{vector_store.document_count}** chunks")

    with col2:
        st.subheader("2. Ask a Question")
        rag_question = st.text_input(
            "Question about your documents",
            placeholder="What is generative AI?",
            key="rag_q",
        )
        if st.button("Search & Answer", key="rag_btn") and rag_question:
            with st.spinner("Retrieving and generating..."):
                try:
                    result = rag_query(rag_question)
                except Exception as exc:
                    st.error(f"RAG request failed: {exc}")
                    result = None

            if result:
                st.subheader("Answer")
                st.write(result["answer"])

                if result["chunks"]:
                    st.subheader("Retrieved Chunks")
                    for i, chunk in enumerate(result["chunks"], 1):
                        with st.expander(
                            f"Chunk {i} — {chunk['metadata'].get('source', '?')} "
                            f"(relevance: {chunk['relevance']})"
                        ):
                            st.write(chunk["text"])

# ── TAB 3: Open Wiki ─────────────────────────────────────────────────
with tab_wiki:
    st.header("Open Wiki — Persistent Knowledge Base")
    st.markdown(
        "**Concept:** Instead of retrieving raw document chunks like RAG, this educational "
        "**Open Wiki demo** converts each source into a persistent markdown topic page and "
        "searches those pages by keywords. It is inspired by "
        "[Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), "
        "but it does not yet perform cross-source synthesis, contradiction detection, or "
        "autonomous wiki maintenance."
    )

    col_compare, col_wiki = st.columns(2)

    with col_compare:
        st.subheader("RAG vs Open Wiki")
        st.markdown(
            """
| | **RAG** | **Open Wiki** |
|---|---|---|
| Storage | Vector chunks | Markdown pages |
| Retrieval | Embedding search | Page search |
| Knowledge | Raw chunks selected per query | Persistent topic pages |
| Readable | Hidden in vector DB | Human-readable files |
            """
        )

    with col_wiki:
        st.subheader("Wiki Status")
        st.caption(f"**{wiki_store.page_count}** pages in `data/wiki/pages/`")
        page_slugs = [s for s in list_pages() if s != "index"]
        if page_slugs:
            with st.expander("Browse pages"):
                for slug in page_slugs:
                    page = wiki_store.get_page(slug)
                    if page:
                        st.markdown(f"- **{page.title}** (`{slug}`)")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Compile Documents")
        if st.button("Compile Sample Docs", key="wiki_compile"):
            with st.spinner("Compiling raw docs into wiki pages..."):
                results = compile_sample_docs()
            if results:
                st.success(f"Compiled: {results}")
            else:
                st.warning("No .txt or .md files found in data/sample_docs/")
        st.caption("Reads `data/sample_docs/` → writes structured pages to `data/wiki/pages/`")

    with col2:
        st.subheader("2. Ask the Wiki")
        wiki_question = st.text_input(
            "Question",
            placeholder="What is the difference between RAG and Open Wiki?",
            key="wiki_q",
        )
        if st.button("Query Wiki", key="wiki_btn") and wiki_question:
            with st.spinner("Searching wiki pages..."):
                try:
                    result = wiki_query(wiki_question)
                except Exception as exc:
                    st.error(f"Wiki query failed: {exc}")
                    result = None

            if result:
                st.subheader("Answer")
                st.write(result["answer"])

                if result["pages"]:
                    st.subheader("Matched Wiki Pages")
                    for i, page in enumerate(result["pages"], 1):
                        with st.expander(
                            f"Page {i} — {page['title']} "
                            f"(relevance: {page['score']})"
                        ):
                            st.caption(f"Slug: `{page['slug']}` | Source: {page.get('source', 'n/a')}")
                            st.write(page["preview"])

    st.divider()
    st.subheader("Try comparing RAG and Open Wiki")
    st.markdown(
        "Ask the **same question** in both the **RAG** tab and **Open Wiki** tab. "
        "RAG returns raw chunks from vector search; Open Wiki returns synthesized wiki pages."
    )

# ── TAB 4: Agent ─────────────────────────────────────────────────────
with tab_agent:
    st.header("AI Agent")
    st.markdown(
        "**Concept:** An agent is an LLM that can **decide** to use tools. "
        "It reasons about what to do, calls tools, observes results, "
        "and loops until it has a final answer. This is the core of Agentic AI."
    )

    st.markdown("**Try these examples:**")
    examples = [
        "What is 15 * 23 + sqrt(144)?",
        "What's the weather in Tokyo?",
        "What time is it right now?",
        "Search the docs: what is RAG?",
        "Search the wiki: what is Open Wiki?",
    ]
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        if cols[i % 2].button(ex, key=f"ex_{i}"):
            st.session_state.agent_query = ex

    agent_query = st.text_input(
        "Agent task",
        value=st.session_state.get("agent_query", ""),
        placeholder="Ask the agent to do something...",
        key="agent_q",
    )

    if st.button("Run Agent", key="agent_btn") and agent_query:
        with st.spinner("Agent is thinking..."):
            try:
                result = Agent().run(agent_query)
            except Exception as exc:
                st.error(f"Agent request failed: {exc}")
                result = None

        if result:
            st.subheader("Final Answer")
            st.success(result.answer)

            st.subheader(f"Reasoning Steps ({result.total_steps})")
            for step in result.steps:
                with st.expander(f"Step {step.step_number}: {step.thought}"):
                    if step.tool_name:
                        st.json({"tool": step.tool_name, "input": step.tool_input})
                        st.code(step.tool_output or "", language="text")

# ── TAB 5: Fine-Tune ─────────────────────────────────────────────────
with tab_finetune:
    st.header("LLM Fine-Tuning with LoRA")
    st.markdown(
        "**Concept:** Specialize a pre-trained model for your task by training small "
        "LoRA adapter weights — cheaper than full fine-tuning."
    )

    try:
        from pathlib import Path as FtPath

        from fine_tuning.src.config import settings as ft_settings
        from fine_tuning.src.dataset import preview_dataset
        from fine_tuning.src.evaluator import evaluate as ft_evaluate
        from fine_tuning.src.inference import generate as ft_generate
        from fine_tuning.src.trainer import train as run_ft_train

        adapter_path = FtPath(ft_settings.output_dir) / ft_settings.adapter_name
        st.caption(f"Base model: `{ft_settings.base_model}` | Adapter: {'✅ trained' if adapter_path.exists() else '❌ not trained yet'}")

        ft_data, ft_train_tab, ft_infer, ft_eval = st.tabs(["Dataset", "Train", "Infer", "Evaluate"])

        with ft_data:
            previews = preview_dataset(FtPath(ft_settings.dataset_path))
            st.write(f"**{len(previews)}** sample examples shown (15 total in dataset)")
            for i, row in enumerate(previews, 1):
                with st.expander(f"Example {i}: {row['instruction'][:50]}..."):
                    st.json({k: v for k, v in row.items() if k != "formatted"})

        with ft_train_tab:
            epochs = st.slider("Epochs", 1, 5, ft_settings.num_epochs, key="ft_epochs")
            st.caption("Training on CPU takes ~5–15 minutes for 3 epochs.")
            if st.button("Start LoRA Training", type="primary", key="ft_train_btn"):
                with st.spinner("Training LoRA adapter..."):
                    result = run_ft_train(num_epochs=epochs)
                st.success("Training complete!")
                st.json({
                    "adapter_path": result.adapter_path,
                    "train_loss": round(result.train_loss, 4) if result.train_loss else None,
                    "eval_loss": round(result.eval_loss, 4) if result.eval_loss else None,
                    "total_steps": result.total_steps,
                })

        with ft_infer:
            ft_instruction = st.text_input("Instruction", "What is LoRA?", key="ft_infer_q")
            if st.button("Generate", key="ft_infer_btn"):
                with st.spinner("Generating..."):
                    result = ft_generate(ft_instruction)
                st.write(f"**Adapter used:** {'Yes ✅' if result.used_adapter else 'No — train first'}")
                st.write(result.response)

        with ft_eval:
            ft_limit = st.slider("Examples", 1, 3, 2, key="ft_eval_limit")
            if st.button("Compare Base vs Fine-Tuned", key="ft_eval_btn"):
                with st.spinner("Evaluating..."):
                    report = ft_evaluate(limit=ft_limit)
                for i, ex in enumerate(report.examples, 1):
                    with st.expander(f"Example {i}: {ex.instruction[:40]}..."):
                        st.markdown(f"**Expected:** {ex.expected}")
                        c1, c2 = st.columns(2)
                        c1.markdown(f"**Base:** {ex.base_response[:300]}")
                        c2.markdown(f"**Fine-tuned:** {ex.finetuned_response[:300]}")

        st.divider()
        st.markdown("📖 Full guide: [fine_tuning/docs/RUN_AND_USE.md](fine_tuning/docs/RUN_AND_USE.md)")

    except ImportError as exc:
        st.error("Fine-tuning dependencies not installed.")
        st.code("pip install -r fine_tuning/requirements.txt", language="bash")
        st.caption(f"Details: {exc}")
    except Exception as exc:
        st.error(f"Fine-tuning error: {exc}")

# ── TAB 6: Concepts ──────────────────────────────────────────────────
with tab_concepts:
    st.header("AI Concepts Covered in This Project")

    concepts = {
        "Generative AI": {
            "what": "AI that creates new content (text, images, code) rather than just classifying.",
            "where": "src/llm/provider.py, src/chat/service.py",
            "try": "Use the Chat tab to talk to the LLM.",
        },
        "Prompt Engineering": {
            "what": "Crafting instructions (system prompts) to guide model behavior.",
            "where": "System prompts in chat/service.py, rag/pipeline.py, agents/agent.py",
            "try": "Edit the system prompt in ChatSession and see how responses change.",
        },
        "RAG": {
            "what": "Retrieval Augmented Generation — search your docs, then generate answers.",
            "where": "src/rag/ (embeddings, vectorstore, pipeline)",
            "try": "Use the RAG tab: ingest docs, then ask questions.",
        },
        "Open Wiki": {
            "what": "Educational, vector-free keyword search over persistent markdown pages compiled one page per source.",
            "where": "src/wiki/ (store, pipeline), data/wiki/pages/",
            "try": "Use the Open Wiki tab: browse pages, compile docs, compare with RAG.",
        },
        "Embeddings": {
            "what": "Converting text to vectors so similar meanings are close in vector space.",
            "where": "src/rag/embeddings.py",
            "try": "Ingest docs and see how semantic search finds relevant chunks.",
        },
        "Vector Database": {
            "what": "Stores embeddings for fast similarity search (ChromaDB).",
            "where": "src/rag/vectorstore.py",
            "try": "Check chunk count in the sidebar after ingesting docs.",
        },
        "AI Agents": {
            "what": "LLMs that autonomously decide to use tools in a reasoning loop.",
            "where": "src/agents/agent.py, src/agents/tools.py",
            "try": "Use the Agent tab with math, weather, or search queries.",
        },
        "Tool Calling": {
            "what": "LLM outputs structured requests to call external functions.",
            "where": "TOOL_SCHEMAS in agents/tools.py, handled in agents/agent.py",
            "try": "Ask the agent to calculate something — watch it call the calculator tool.",
        },
        "MCP": {
            "what": "Model Context Protocol — standard way for AI apps to connect to tools/data.",
            "where": "src/mcp/server.py",
            "try": "Run: python -m src.mcp.server (connect from Cursor or Claude Desktop).",
        },
        "Fine-Tuning (LoRA)": {
            "what": "Train small adapter weights to specialize a model for your task.",
            "where": "fine_tuning/src/trainer.py, fine_tuning/app.py",
            "try": "Use the Fine-Tune tab: train → infer → evaluate.",
        },
    }

    for name, info in concepts.items():
        with st.expander(f"**{name}**"):
            st.markdown(f"**What:** {info['what']}")
            st.markdown(f"**Code:** `{info['where']}`")
            st.markdown(f"**Try it:** {info['try']}")

    st.divider()
    st.subheader("How Everything Connects")
    st.markdown(
        "The main app is **one integrated product**. Chat, RAG, Open Wiki, and Agent share the same "
        "LLM. The Agent's `search_knowledge` tool uses the RAG pipeline; `search_wiki` uses the Open Wiki. "
        "MCP exposes the same tools to external apps like Cursor."
    )
    st.code("""
┌─────────────────────────────────────────────────────────────────────┐
│                 MAIN INTEGRATED PRODUCT (app.py)                     │
│                                                                      │
│  ┌─────────┐   ┌─────────┐   ┌──────────┐   ┌─────────┐   ┌──────────┐   ┌──────────┐ │
│  │  CHAT   │   │   RAG   │   │OPEN WIKI │   │  AGENT  │   │FINE-TUNE │   │ CONCEPTS │ │
│  │  Tab    │   │  Tab    │   │   Tab    │   │  Tab    │   │   Tab    │   │   Tab    │ │
│  └────┬────┘   └────┬────┘   └────┬─────┘   └────┬────┘   └────┬─────┘   └──────────┘ │
│       │             │             │             │                                      │
│       ▼             ▼             ▼             ▼                                      │
│  chat/service   rag/pipeline   wiki/pipeline  agents/agent                             │
│       │             ▲             ▲             │                                      │
│       │             │             │        agents/tools                                │
│       │             │             │             │                                      │
│       │             └── search_knowledge ◄──────┤                                      │
│       │                   search_wiki ◄─────────┘                                      │
│       │                                                              │
│       └─────────────────┬───────────────────┘                       │
│                         ▼                                            │
│                ┌─────────────────┐                                  │
│                │  LLM Provider   │  ◄── shared brain                  │
│                │ Ollama/OpenAI/  │                                  │
│                │   Demo Mode     │                                  │
│                └────────┬────────┘                                  │
│                         │                                            │
│           ┌─────────────┼─────────────┐                           │
│           ▼             ▼             ▼                             │
│    ┌────────────┐ ┌───────────┐ ┌──────────────┐                   │
│    │ Embeddings │ │ ChromaDB  │ │ MCP Server   │                   │
│    │ (vectors)  │ │ (vectors) │ │ (separate    │                   │
│    └────────────┘ └───────────┘ │  process)    │                   │
│                                  │ same tools + │                   │
│                                  │ rag_search   │                   │
│                                  └──────┬───────┘                   │
│                                         │                            │
│                                  Cursor / Claude                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  FINE-TUNING: fine_tuning/ — LoRA train, infer, evaluate (in-app tab)│
│  DOMAIN APP: medical_assistant/ — Healthcare Chat, RAG, Agent, MCP │
└─────────────────────────────────────────────────────────────────────┘

Full diagram: docs/INTEGRATION_DIAGRAM.md
    """, language="text")
