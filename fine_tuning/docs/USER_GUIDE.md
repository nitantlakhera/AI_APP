# Fine-Tuning User Guide

Complete guide for using the **LLM Fine-Tuning Lab** module.

---

## Table of Contents

1. [What Is Fine-Tuning?](#1-what-is-fine-tuning)
2. [Installation](#2-installation)
3. [Configuration](#3-configuration)
4. [Understanding the Dataset](#4-understanding-the-dataset)
5. [Training](#5-training)
6. [Inference](#6-inference)
7. [Evaluation](#7-evaluation)
8. [Web UI](#8-web-ui)
9. [Scaling Up](#9-scaling-up)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. What Is Fine-Tuning?

**Pre-trained LLM** → already knows language from billions of tokens  
**Fine-tuning** → teach it your specific style, format, or domain

### Fine-Tuning vs Other Techniques

| Technique | What It Does | When to Use |
|-----------|-------------|-------------|
| **Prompting** | Instructions in the prompt | Quick, no training needed |
| **RAG** | Retrieve docs at query time | Private/current knowledge |
| **Fine-tuning** | Change model weights | Consistent style, specialized task |
| **LoRA** | Fine-tune cheaply (this module) | Limited GPU/CPU, small datasets |

### What This Module Teaches

- How to prepare instruction data (JSONL)
- How LoRA adapters work
- How to train, save, and load adapters
- How to compare base vs fine-tuned outputs

---

## 2. Installation

```bash
cd C:\Users\nila0425\Downloads\AI_APP

# Install fine-tuning dependencies (separate from main app)
pip install -r fine_tuning/requirements.txt

# Create config
copy fine_tuning\.env.example fine_tuning\.env
```

**Note:** First run downloads `distilgpt2` from Hugging Face (~350 MB).

### Hardware Requirements

| Setup | RAM | Time (3 epochs) |
|-------|-----|-----------------|
| CPU only | 4 GB+ | ~5–15 minutes |
| GPU (CUDA) | 4 GB VRAM+ | ~1–3 minutes |

---

## 3. Configuration

Edit `fine_tuning/.env`:

```env
BASE_MODEL=distilgpt2
OUTPUT_DIR=./fine_tuning/outputs
DATASET_PATH=./fine_tuning/data/sample_dataset.jsonl
NUM_EPOCHS=3
BATCH_SIZE=2
LEARNING_RATE=2e-4
MAX_SEQ_LENGTH=256

# LoRA
LORA_R=8
LORA_ALPHA=16
LORA_DROPOUT=0.05

DEVICE=auto
```

### Key Parameters Explained

| Parameter | What It Does | Beginner Tip |
|-----------|-------------|--------------|
| `NUM_EPOCHS` | How many times to see full dataset | Start with 3; increase if underfitting |
| `BATCH_SIZE` | Examples per training step | Lower if out-of-memory |
| `LEARNING_RATE` | Step size for weight updates | 1e-4 to 3e-4 is typical for LoRA |
| `LORA_R` | Rank of adapter matrices | Higher = more capacity, more memory |
| `MAX_SEQ_LENGTH` | Max tokens per example | Increase for longer answers |

---

## 4. Understanding the Dataset

### JSONL Format

Each line is one JSON object:

```json
{"instruction": "What is LoRA?", "input": "", "output": "LoRA is a parameter-efficient fine-tuning method..."}
```

| Field | Required | Description |
|-------|----------|-------------|
| `instruction` | Yes | What you want the model to do |
| `input` | No | Extra context (can be empty `""`) |
| `output` | Yes | The ideal response the model should learn |

### Formatted Training Text (Alpaca Style)

```
### Instruction:
What is LoRA?

### Response:
LoRA is a parameter-efficient fine-tuning method...
```

### Create Your Own Dataset

1. Copy `fine_tuning/data/sample_dataset.jsonl`
2. Add rows (aim for 50–500+ for real tasks)
3. Update `DATASET_PATH` in `.env`
4. Re-run training

**Tips:**
- Keep instructions clear and consistent
- Match the output style you want at inference time
- Include diverse examples of the same task type

---

## 5. Training

### Command Line

```bash
python fine_tuning/scripts/train.py
```

### What Happens During Training

1. Load `distilgpt2` base model
2. Attach LoRA adapters to attention layers
3. Tokenize dataset into train/eval splits (80/20)
4. Train for N epochs, saving best checkpoint
5. Save adapter to `fine_tuning/outputs/lora_adapter/`

### Expected Output

```
Training complete!
  Base model:    distilgpt2
  Adapter saved: fine_tuning/outputs/lora_adapter
  Train loss:    2.3456
  Eval loss:     2.1234
  Total steps:   24
```

**Lower loss** generally means better fit — but watch for overfitting (train loss drops, eval loss rises).

---

## 6. Inference

### Command Line

```bash
python fine_tuning/scripts/infer.py "What is fine-tuning?"
```

### In Python

```python
from fine_tuning.src.inference import generate

result = generate("Explain LoRA in one sentence.")
print(result.response)
print("Used adapter:", result.used_adapter)
```

### With vs Without Adapter

| Mode | Behavior |
|------|----------|
| No adapter saved | Uses base `distilgpt2` only |
| Adapter exists | Loads LoRA weights on top of base model |

---

## 7. Evaluation

```bash
python fine_tuning/scripts/evaluate.py
```

Compares **base model** vs **fine-tuned model** on sample instructions:

```
--- Example 1 ---
Instruction: What is LoRA?
Expected:    LoRA (Low-Rank Adaptation) is...
Base model:  LoRA stands for...
Fine-tuned:  LoRA (Low-Rank Adaptation) is a parameter-efficient...
```

Use this deterministic, greedy-decoding comparison to inspect possible changes
in format and content alignment. It is qualitative: the demo does not calculate
an accuracy score and does not prove that the fine-tuned model is generally better.

---

## 8. Web UI

```bash
streamlit run fine_tuning/app.py
```

Four tabs:
- **Dataset** — preview training examples
- **Train** — start LoRA training with slider for epochs
- **Infer** — test generation
- **Evaluate** — side-by-side base vs fine-tuned comparison

---

## 9. Scaling Up

### Use a Larger Model

```env
BASE_MODEL=meta-llama/Llama-3.2-1B
DEVICE=cuda
BATCH_SIZE=1
```

Requires Hugging Face access token for gated models and a GPU.

### More Data

- 15 examples: learning/demo
- 100–500 examples: small specialized task
- 1000+ examples: production-quality specialization

### Full Fine-Tuning (Advanced)

LoRA is recommended for beginners. Full fine-tuning updates all weights — needs large GPU and more data. This module focuses on LoRA as the practical starting point.

---

## 10. Troubleshooting

| Problem | Solution |
|---------|----------|
| `CUDA out of memory` | Set `BATCH_SIZE=1`, `DEVICE=cpu`, or use smaller model |
| Training very slow | Normal on CPU; reduce `NUM_EPOCHS` or use GPU |
| Adapter not used in inference | Run `train.py` first; check `outputs/lora_adapter/` exists |
| Nonsense outputs | Model too small or too few epochs; try more data/epochs |
| `ModuleNotFoundError: torch` | Run `pip install -r fine_tuning/requirements.txt` |
| Hugging Face download fails | Check internet; set `HF_TOKEN` for gated models |

---

## Related Docs

- [Architecture Guide](ARCHITECTURE.md)
- [Call Flow Guide](CALL_FLOW.md)
- [Main AI Learning Lab](../../docs/USER_GUIDE.md)
