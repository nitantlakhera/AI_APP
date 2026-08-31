"""CLI script to run inference with fine-tuned model."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from fine_tuning.src.inference import generate


def main() -> None:
    instruction = " ".join(sys.argv[1:]) or "What is LoRA?"
    print(f"Instruction: {instruction}\n")

    result = generate(instruction)

    print(f"Model:   {result.model_path}")
    print(f"Adapter: {'Yes' if result.used_adapter else 'No (base model)'}")
    print(f"\nResponse:\n{result.response}")


if __name__ == "__main__":
    main()
