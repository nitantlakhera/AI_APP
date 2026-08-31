"""Streamlit UI for the fine-tuning module."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st

from fine_tuning.src.config import settings
from fine_tuning.src.dataset import preview_dataset
from fine_tuning.src.evaluator import evaluate
from fine_tuning.src.inference import generate
from fine_tuning.src.trainer import train

st.set_page_config(page_title="LLM Fine-Tuning Lab", page_icon="🎯", layout="wide")

st.title("🎯 LLM Fine-Tuning Lab")
st.caption("Learn parameter-efficient fine-tuning with LoRA")

with st.sidebar:
    st.subheader("Settings")
    st.write(f"**Base model:** `{settings.base_model}`")
    st.write(f"**Dataset:** `{settings.dataset_path}`")
    st.write(f"**Output:** `{settings.output_dir}`")
    adapter = Path(settings.output_dir) / settings.adapter_name
    st.write(f"**Adapter:** {'✅ Ready' if adapter.exists() else '❌ Not trained'}")
    st.divider()
    st.markdown("**Learning guides**")
    st.caption("Open `docs/html/fine-tuning-flow.html` for the visual flow.")
    st.code(r"start docs\html\fine-tuning-flow.html", language="powershell")
    st.caption("Detailed guides are in `fine_tuning/docs/`.")

tab_data, tab_train, tab_infer, tab_eval, tab_learn = st.tabs([
    "📂 Dataset", "🏋️ Train", "💬 Infer", "📊 Evaluate", "📖 Learn"
])

with tab_data:
    st.header("Training Dataset")
    st.markdown(
        "Each row has **instruction**, optional **input**, and **output**. "
        "The model learns to produce the output given the instruction."
    )
    try:
        previews = preview_dataset(Path(settings.dataset_path))
        for i, row in enumerate(previews, 1):
            with st.expander(f"Example {i}: {row['instruction'][:60]}..."):
                st.json({k: v for k, v in row.items() if k != "formatted"})
                st.code(row["formatted"], language="text")
    except Exception as exc:
        st.error(str(exc))

with tab_train:
    st.header("Train LoRA Adapter")
    st.markdown(
        "**Concept:** LoRA trains small adapter weights on top of a frozen base model. "
        "Much cheaper than full fine-tuning."
    )
    epochs = st.slider("Epochs", 1, 10, settings.num_epochs)

    if st.button("Start Training", type="primary"):
        with st.spinner("Training... this may take a few minutes on CPU"):
            try:
                result = train(num_epochs=epochs)
                st.success("Training complete!")
                st.json({
                    "base_model": result.base_model,
                    "adapter_path": result.adapter_path,
                    "train_loss": result.train_loss,
                    "eval_loss": result.eval_loss,
                    "total_steps": result.total_steps,
                })
            except Exception as exc:
                st.error(f"Training failed: {exc}")

with tab_infer:
    st.header("Run Inference")
    instruction = st.text_input("Instruction", "What is LoRA?")
    user_input = st.text_input("Input (optional)", "")

    if st.button("Generate"):
        with st.spinner("Generating..."):
            try:
                result = generate(instruction, user_input)
                st.write(f"**Adapter used:** {'Yes' if result.used_adapter else 'No'}")
                st.write(result.response)
            except Exception as exc:
                st.error(str(exc))

with tab_eval:
    st.header("Compare Base vs Fine-Tuned")
    limit = st.slider("Examples to compare", 1, 5, 3)

    if st.button("Run Evaluation"):
        with st.spinner("Evaluating..."):
            try:
                report = evaluate(limit=limit)
                for i, ex in enumerate(report.examples, 1):
                    with st.expander(f"Example {i}: {ex.instruction[:50]}..."):
                        st.markdown(f"**Expected:** {ex.expected}")
                        col1, col2 = st.columns(2)
                        col1.markdown(f"**Base:** {ex.base_response}")
                        col2.markdown(f"**Fine-tuned:** {ex.finetuned_response}")
            except Exception as exc:
                st.error(str(exc))

with tab_learn:
    st.header("Fine-Tuning Concepts")
    st.markdown("""
    | Concept | What it means |
    |---------|--------------|
    | **Fine-tuning** | Adapt a pre-trained model to your specific task |
    | **LoRA** | Train only ~1% of weights (cheap, fast) |
    | **Instruction data** | JSONL with instruction + output pairs |
    | **Adapter** | Small weight file saved after training |
    | **Base vs Fine-tuned** | Compare before/after in Evaluate tab |

    **Pipeline:** Dataset → Tokenize → LoRA Train → Save Adapter → Infer / Evaluate
    """)
    st.code("""
JSONL → dataset.py → trainer.py (LoRA) → outputs/lora_adapter/
                                              │
                         ┌────────────────────┼────────────────────┐
                         ▼                    ▼                    ▼
                   inference.py          evaluator.py          export.py
    """, language="text")
    st.markdown("📖 [Full guide](docs/RUN_AND_USE.md) | [Architecture](docs/ARCHITECTURE.md)")
