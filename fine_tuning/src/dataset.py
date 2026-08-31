"""Dataset loading and formatting for instruction fine-tuning."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from datasets import Dataset


@dataclass
class TrainingExample:
    """One instruction-tuning example."""

    instruction: str
    input: str
    output: str

    def to_prompt(self) -> str:
        """Format as an Alpaca-style training prompt."""
        if self.input.strip():
            return (
                "### Instruction:\n"
                f"{self.instruction}\n\n"
                "### Input:\n"
                f"{self.input}\n\n"
                "### Response:\n"
                f"{self.output}"
            )
        return (
            "### Instruction:\n"
            f"{self.instruction}\n\n"
            "### Response:\n"
            f"{self.output}"
        )

    def to_inference_prompt(self) -> str:
        """Prompt for generation (without the answer)."""
        if self.input.strip():
            return (
                "### Instruction:\n"
                f"{self.instruction}\n\n"
                "### Input:\n"
                f"{self.input}\n\n"
                "### Response:\n"
            )
        return (
            "### Instruction:\n"
            f"{self.instruction}\n\n"
            "### Response:\n"
        )


def load_jsonl(path: Path) -> list[TrainingExample]:
    """Load training examples from a JSONL file."""
    examples: list[TrainingExample] = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            examples.append(
                TrainingExample(
                    instruction=row.get("instruction", ""),
                    input=row.get("input", ""),
                    output=row.get("output", ""),
                )
            )
    if not examples:
        raise ValueError(f"No training examples found in {path}")
    return examples


def build_dataset(path: Path, train_split: float = 0.8) -> dict[str, Dataset]:
    """
    Load JSONL data and split into train/eval HuggingFace datasets.

  Concept: Instruction Fine-Tuning Data
  - Each row teaches the model: given instruction (+ optional input) → produce output
  - Alpaca format is widely used and easy to understand
    """
    examples = load_jsonl(path)
    records = [{"text": ex.to_prompt()} for ex in examples]

    dataset = Dataset.from_list(records)
    split = dataset.train_test_split(test_size=1 - train_split, seed=42)
    return {"train": split["train"], "eval": split["test"]}


def preview_dataset(path: Path, limit: int = 3) -> list[dict[str, str]]:
    """Return a few formatted examples for documentation / UI preview."""
    return [
        {
            "instruction": ex.instruction,
            "input": ex.input,
            "output": ex.output,
            "formatted": ex.to_prompt(),
        }
        for ex in load_jsonl(path)[:limit]
    ]
