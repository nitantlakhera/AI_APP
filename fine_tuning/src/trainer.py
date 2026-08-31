"""LoRA fine-tuning trainer using Hugging Face Transformers + PEFT."""

from __future__ import annotations

import inspect
import math
from dataclasses import dataclass
from pathlib import Path

import torch
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

from fine_tuning.src.config import settings
from fine_tuning.src.dataset import build_dataset


@dataclass
class TrainResult:
    """Summary returned after training completes."""

    output_dir: str
    train_loss: float | None
    eval_loss: float | None
    total_steps: int
    base_model: str
    adapter_path: str


def _resolve_device() -> str:
    if settings.device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return settings.device


def _tokenize_dataset(dataset_dict: dict, tokenizer) -> dict:
    """Tokenize text field for causal language modeling."""

    def tokenize(batch: dict) -> dict:
        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=settings.max_seq_length,
            padding="max_length",
        )

    return {
        split: dataset_dict[split].map(tokenize, batched=True, remove_columns=["text"])
        for split in dataset_dict
    }


def train(
    dataset_path: Path | None = None,
    output_dir: Path | None = None,
    num_epochs: int | None = None,
) -> TrainResult:
    """
    Fine-tune a base LLM with LoRA adapters.

    Concept: Parameter-Efficient Fine-Tuning (PEFT)
    - Full fine-tuning updates ALL model weights (expensive, needs GPU)
    - LoRA adds small trainable matrices to attention layers (cheap, CPU-friendly)
    - Only ~1% of parameters are trained, but model learns your task
    """
    dataset_path = dataset_path or Path(settings.dataset_path)
    output_dir = output_dir or Path(settings.output_dir)
    adapter_dir = output_dir / settings.adapter_name
    adapter_dir.mkdir(parents=True, exist_ok=True)

    device = _resolve_device()
    epochs = settings.num_epochs if num_epochs is None else num_epochs
    if epochs <= 0:
        raise ValueError("num_epochs must be greater than zero")

    # 1. Load tokenizer and base model
    tokenizer = AutoTokenizer.from_pretrained(settings.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(settings.base_model)
    model.config.pad_token_id = tokenizer.pad_token_id

    # 2. Apply LoRA adapters
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=settings.lora_r,
        lora_alpha=settings.lora_alpha,
        lora_dropout=settings.lora_dropout,
        target_modules=["c_attn"] if "gpt" in settings.base_model.lower() else ["q_proj", "v_proj"],
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # 3. Prepare dataset
    raw_datasets = build_dataset(dataset_path)
    tokenized = _tokenize_dataset(raw_datasets, tokenizer)
    train_size = len(tokenized["train"])
    steps_per_epoch = max(1, math.ceil(train_size / settings.batch_size))
    total_steps = max(1, steps_per_epoch * epochs)
    warmup_steps = max(1, int(total_steps * settings.warmup_ratio))
    save_steps = max(1, min(settings.save_steps, steps_per_epoch))

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    training_kwargs = dict(
        output_dir=str(output_dir),
        num_train_epochs=epochs,
        per_device_train_batch_size=settings.batch_size,
        per_device_eval_batch_size=settings.batch_size,
        learning_rate=settings.learning_rate,
        warmup_steps=warmup_steps,
        weight_decay=settings.weight_decay,
        logging_steps=max(1, min(settings.logging_steps, total_steps)),
        save_steps=save_steps,
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to="none",
        seed=settings.seed,
        use_cpu=(device == "cpu"),
        fp16=(device == "cuda"),
    )
    strategy_parameter = (
        "eval_strategy"
        if "eval_strategy" in inspect.signature(TrainingArguments).parameters
        else "evaluation_strategy"
    )
    training_kwargs[strategy_parameter] = "epoch"
    training_args = TrainingArguments(**training_kwargs)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["eval"],
        data_collator=data_collator,
    )

    train_output = trainer.train()
    eval_metrics = trainer.evaluate()

    # 6. Save LoRA adapter + tokenizer
    model.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))

    return TrainResult(
        output_dir=str(output_dir),
        train_loss=train_output.training_loss,
        eval_loss=eval_metrics.get("eval_loss"),
        total_steps=train_output.global_step,
        base_model=settings.base_model,
        adapter_path=str(adapter_dir),
    )
