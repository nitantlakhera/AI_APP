"""CLI script to compare base vs fine-tuned model."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from fine_tuning.src.evaluator import evaluate


def main() -> None:
    print("=" * 60)
    print("AI Learning Lab — Fine-Tuning Evaluation")
    print("=" * 60)

    report = evaluate(limit=3)

    for i, ex in enumerate(report.examples, 1):
        print(f"\n--- Example {i} ---")
        print(f"Instruction: {ex.instruction}")
        print(f"Expected:    {ex.expected}")
        print(f"Base model:  {ex.base_response[:200]}")
        print(f"Fine-tuned:  {ex.finetuned_response[:200]}")

    print(f"\nAdapter: {report.adapter_path}")
    print("Done.")


if __name__ == "__main__":
    main()
