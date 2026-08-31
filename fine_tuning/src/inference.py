"""Run inference with base model or fine-tuned LoRA adapter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from fine_tuning.src.config import settings
from fine_tuning.src.dataset import TrainingExample


@dataclass
class GenerationResult:
    """Output from model generation."""

    prompt: str
    response: str
    model_path: str
    used_adapter: bool


def _resolve_device() -> str:
    if settings.device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return settings.device


def _load_model(adapter_path: Path | None = None):
    """Load base model, optionally with LoRA adapter merged on top."""
    device = _resolve_device()
    tokenizer = AutoTokenizer.from_pretrained(settings.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    base_model = AutoModelForCausalLM.from_pretrained(settings.base_model)
    used_adapter = False

    if adapter_path and adapter_path.exists():
        model = PeftModel.from_pretrained(base_model, str(adapter_path))
        used_adapter = True
    else:
        model = base_model

    model.to(device)
    model.eval()
    return model, tokenizer, device, used_adapter


def generate(
    instruction: str,
    user_input: str = "",
    adapter_path: Path | None = None,
    max_new_tokens: int = 100,
    use_adapter: bool = True,
    do_sample: bool = True,
) -> GenerationResult:
    """
    Generate a response from the model.

    Concept: Inference after Fine-Tuning
    - Base model: general knowledge, may not follow your format
    - Fine-tuned adapter: specialized on your instruction dataset
    """
    example = TrainingExample(instruction=instruction, input=user_input, output="")
    prompt = example.to_inference_prompt()

    adapter = adapter_path or Path(settings.output_dir) / settings.adapter_name
    selected_adapter = adapter if use_adapter and adapter.exists() else None
    model, tokenizer, device, used_adapter = _load_model(selected_adapter)

    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    generation_options = {
        "max_new_tokens": max_new_tokens,
        "do_sample": do_sample,
        "pad_token_id": tokenizer.pad_token_id,
    }
    if do_sample:
        generation_options.update({"temperature": 0.7, "top_p": 0.9})

    with torch.no_grad():
        outputs = model.generate(**inputs, **generation_options)

    input_token_count = inputs["input_ids"].shape[1]
    generated_tokens = outputs[0][input_token_count:]
    response = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

    return GenerationResult(
        prompt=prompt,
        response=response,
        model_path=settings.base_model,
        used_adapter=used_adapter,
    )
