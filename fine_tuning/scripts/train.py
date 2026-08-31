"""CLI script to fine-tune a model with LoRA."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from fine_tuning.src.trainer import train


def main() -> None:
    print("=" * 60)
    print("AI Learning Lab — LoRA Fine-Tuning")
    print("=" * 60)

    result = train()

    print("\nTraining complete!")
    print(f"  Base model:    {result.base_model}")
    print(f"  Adapter saved: {result.adapter_path}")
    print(f"  Train loss:    {result.train_loss:.4f}" if result.train_loss else "  Train loss:    N/A")
    print(f"  Eval loss:     {result.eval_loss:.4f}" if result.eval_loss else "  Eval loss:     N/A")
    print(f"  Total steps:   {result.total_steps}")
    print("\nNext: python fine_tuning/scripts/evaluate.py")


if __name__ == "__main__":
    main()
