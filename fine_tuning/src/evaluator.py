"""Evaluate base model vs fine-tuned adapter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fine_tuning.src.config import settings
from fine_tuning.src.dataset import TrainingExample, load_jsonl
from fine_tuning.src.inference import generate


@dataclass
class EvalExample:
    """Comparison for one test example."""

    instruction: str
    expected: str
    base_response: str
    finetuned_response: str


@dataclass
class EvalReport:
    """Evaluation summary."""

    examples: list[EvalExample]
    adapter_path: str
    base_model: str


def evaluate(
    dataset_path: Path | None = None,
    adapter_path: Path | None = None,
    limit: int = 5,
) -> EvalReport:
    """
    Compare base model vs fine-tuned model on sample instructions.

    Concept: Evaluation
    - Compare outputs before and after fine-tuning
    - Check if model follows instruction format and gives expected style
  - For production, use automated metrics (BLEU, ROUGE, LLM-as-judge)
    """
    dataset_path = dataset_path or Path(settings.dataset_path)
    adapter_path = adapter_path or Path(settings.output_dir) / settings.adapter_name
    if not adapter_path.exists():
        raise FileNotFoundError(
            f"No fine-tuned adapter found at {adapter_path}. Train the model before evaluation."
        )

    examples = load_jsonl(dataset_path)[:limit]
    results: list[EvalExample] = []

    for ex in examples:
        # Greedy decoding keeps the base-vs-adapter comparison reproducible.
        base = generate(ex.instruction, ex.input, use_adapter=False, do_sample=False)
        tuned = generate(
            ex.instruction,
            ex.input,
            adapter_path=adapter_path,
            do_sample=False,
        )

        results.append(
            EvalExample(
                instruction=ex.instruction,
                expected=ex.output,
                base_response=base.response,
                finetuned_response=tuned.response,
            )
        )

    return EvalReport(
        examples=results,
        adapter_path=str(adapter_path),
        base_model=settings.base_model,
    )
