# Fine-Tuning Module — How to Run and Use

Complete guide for the **LLM Fine-Tuning Lab**.

---

## 1. Install

```bash
cd C:\Users\nila0425\Downloads\AI_APP

# Main app deps (if not installed)
pip install -r requirements.txt

# Fine-tuning deps (PyTorch, PEFT, etc.)
pip install -r fine_tuning/requirements.txt

# Optional config
copy fine_tuning\.env.example fine_tuning\.env
```

**Note:** First run downloads `distilgpt2` (~350 MB) from Hugging Face.

---

## 2. Run Options

### Option A: Standalone app

```bash
python -m streamlit run fine_tuning/app.py
```

### Option B: Main app Fine-Tune tab

```bash
python -m streamlit run app.py
```

Open the **Fine-Tune** tab (requires fine-tuning dependencies installed).

### Option C: Command line

```bash
python fine_tuning/scripts/train.py
python fine_tuning/scripts/evaluate.py
python fine_tuning/scripts/infer.py "What is LoRA?"
python fine_tuning/scripts/export.py
```

---

## 3. How to Use — Step by Step

### Step 1: Preview dataset
- Open **Dataset** tab
- Review 15 instruction examples (AI concepts)
- Format: instruction → output (Alpaca style)

### Step 2: Train LoRA adapter
- Open **Train** tab
- Set epochs (start with 3)
- Click **Start Training**
- Wait 5–15 minutes on CPU
- Output saved to `fine_tuning/outputs/lora_adapter/`

### Step 3: Run inference
- Open **Infer** tab
- Enter: `What is LoRA?`
- Click **Generate**
- **Adapter used: Yes** means fine-tuned weights loaded

### Step 4: Evaluate
- Open **Evaluate** tab
- Click **Run Evaluation**
- Compare **Base** vs **Fine-tuned** side by side

### Step 5: Export (optional)
```bash
python fine_tuning/scripts/export.py
```
Merges adapter into full model at `fine_tuning/outputs/merged_model/`

---

## 4. What Each File Does

| File | Purpose |
|------|---------|
| `src/dataset.py` | Load JSONL, format prompts, train/eval split |
| `src/trainer.py` | LoRA training with Hugging Face Trainer |
| `src/inference.py` | Generate with base or fine-tuned model |
| `src/evaluator.py` | Compare base vs fine-tuned |
| `scripts/train.py` | CLI training |
| `scripts/export.py` | Merge adapter to full model |
| `data/sample_dataset.jsonl` | 15 training examples |

---

## 5. Configuration (`fine_tuning/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_MODEL` | distilgpt2 | Hugging Face model ID |
| `NUM_EPOCHS` | 3 | Training epochs |
| `BATCH_SIZE` | 2 | Batch size |
| `LEARNING_RATE` | 2e-4 | LoRA learning rate |
| `LORA_R` | 8 | LoRA rank |
| `DEVICE` | auto | cpu / cuda / auto |

---

## 6. Learning Exercises

1. **Train with 1 epoch** — see underfitting
2. **Train with 5 epochs** — compare eval loss
3. **Add your own JSONL row** — retrain, test inference
4. **Run evaluate** — see if fine-tuned follows instruction format better
5. **Read `src/trainer.py`** — find LoRA config and target modules
6. **Export merged model** — understand adapter vs full weights

---

## 7. Troubleshooting

| Problem | Solution |
|---------|----------|
| `No module named 'peft'` | `pip install -r fine_tuning/requirements.txt` |
| Training slow | Normal on CPU; use 1 epoch for quick tests |
| Poor output quality | distilgpt2 is tiny — for learning flow only; use larger model + GPU for quality |
| Adapter not found | Run `train.py` first |
| CUDA OOM | `BATCH_SIZE=1`, `DEVICE=cpu` |
| `warmup_ratio` error | Update trainer.py (fixed in latest version) |

---

## 8. Relation to Main Project

| Main Lab | Fine-Tuning Lab |
|----------|-----------------|
| Uses pre-trained LLM as-is | Teaches how to specialize an LLM |
| RAG adds external knowledge | Fine-tuning changes model behavior |
| Prompt engineering | Weight adaptation |

**Together:** RAG + fine-tuning + agents = complete production AI stack.

---

## Related Docs

- [User Guide](USER_GUIDE.md)
- [Architecture](ARCHITECTURE.md)
- [Call Flow](CALL_FLOW.md)
- [Main Run & Use](../../docs/RUN_AND_USE.md)
