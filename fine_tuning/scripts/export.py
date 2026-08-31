"""Export merged model — combine LoRA adapter with base model."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from fine_tuning.src.config import settings


def merge_and_export(export_dir: Path | None = None) -> str:
    """
    Merge LoRA adapter into base model and save full weights.

    Concept: After training, you can merge adapters for easier deployment
    without needing PEFT at inference time.
    """
    adapter_path = Path(settings.output_dir) / settings.adapter_name
    if not adapter_path.exists():
        raise FileNotFoundError(
            f"No adapter found at {adapter_path}. Run train.py first."
        )

    export_dir = export_dir or Path(settings.output_dir) / "merged_model"
    export_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading base model: {settings.base_model}")
    base = AutoModelForCausalLM.from_pretrained(settings.base_model)
    tokenizer = AutoTokenizer.from_pretrained(settings.base_model)

    print(f"Loading adapter: {adapter_path}")
    model = PeftModel.from_pretrained(base, str(adapter_path))

    print("Merging weights...")
    merged = model.merge_and_unload()

    print(f"Saving to: {export_dir}")
    merged.save_pretrained(str(export_dir))
    tokenizer.save_pretrained(str(export_dir))

    return str(export_dir)


def main() -> None:
    path = merge_and_export()
    print(f"\nMerged model saved to: {path}")
    print("You can load it with: AutoModelForCausalLM.from_pretrained(path)")


if __name__ == "__main__":
    main()
