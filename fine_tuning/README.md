# LLM Fine-Tuning Lab

A beginner-friendly module for learning **LLM fine-tuning** with **LoRA** (Low-Rank Adaptation).

This folder is separate from the main AI Learning Lab app but complements it — after learning generative AI, RAG, and agents, you learn how to **specialize** a model for your own task.

## What You'll Learn

| Concept | Description |
|---------|-------------|
| **Fine-Tuning** | Adapting a pre-trained model to a specific task |
| **LoRA / PEFT** | Train only ~1% of weights — fast and cheap |
| **Instruction Data** | Alpaca-style JSONL format (instruction + output) |
| **Training Loop** | Epochs, loss, evaluation, checkpointing |
| **Inference** | Generate with base model vs fine-tuned adapter |
| **Evaluation** | Compare before/after fine-tuning |

## Quick Start

```bash
# From project root (AI_APP)
pip install -r fine_tuning/requirements.txt

# Copy config
copy fine_tuning\.env.example fine_tuning\.env

# Train (uses distilgpt2 — runs on CPU)
python fine_tuning/scripts/train.py

# Compare base vs fine-tuned
python fine_tuning/scripts/evaluate.py

# Run inference
python fine_tuning/scripts/infer.py "What is LoRA?"

# Or use the web UI
streamlit run fine_tuning/app.py
```

## Project Structure

```
fine_tuning/
├── app.py                  # Streamlit UI
├── requirements.txt        # ML dependencies (torch, peft, etc.)
├── .env.example            # Configuration
│
├── src/
│   ├── config.py           # Settings
│   ├── dataset.py          # Load & format JSONL data
│   ├── trainer.py          # LoRA training loop
│   ├── inference.py        # Generate text
│   └── evaluator.py        # Compare base vs fine-tuned
│
├── data/
│   └── sample_dataset.jsonl  # 15 AI concept examples
│
├── scripts/
│   ├── train.py
│   ├── evaluate.py
│   └── infer.py
│
├── outputs/                # Created after training (gitignored)
│   └── lora_adapter/
│
└── docs/
    ├── USER_GUIDE.md
    ├── ARCHITECTURE.md
    └── CALL_FLOW.md
```

## Architecture (High Level)

```
JSONL Dataset → Tokenizer → LoRA Training → Adapter Weights
                                                    │
Base Model (distilgpt2) ────────────────────────────┘
                                                    │
                                              Inference / Evaluation
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full details.

## Default Model

**`distilgpt2`** — a small model (~80M parameters) chosen because:
- Runs on CPU (no GPU required)
- Trains in minutes, not hours
- Perfect for learning the fine-tuning workflow

For production, swap to larger models (Llama, Mistral) in `.env` — same code, more compute needed.

## Documentation

- [How to Run and Use](docs/RUN_AND_USE.md) — **start here**
- [User Guide](docs/USER_GUIDE.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Integration Diagram](docs/INTEGRATION_DIAGRAM.md)
- [Call Flow Guide](docs/CALL_FLOW.md)

## Export Merged Model

```bash
python fine_tuning/scripts/export.py
```

Saves full merged weights to `fine_tuning/outputs/merged_model/`.

## Link to Main Project

After fine-tuning, you can:
1. Export merged weights and serve via Ollama (advanced)
2. Use the fine-tuned model in your own Python apps via `inference.py`
3. Compare how fine-tuning differs from RAG (RAG = external knowledge, fine-tuning = changed model behavior)
