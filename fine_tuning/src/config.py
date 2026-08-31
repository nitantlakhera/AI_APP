"""Fine-tuning configuration."""

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

MODULE_ROOT = Path(__file__).resolve().parent.parent


class FineTuneSettings(BaseSettings):
    """Settings for the fine-tuning pipeline."""

    model_config = SettingsConfigDict(
        env_file=MODULE_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Model
    base_model: str = "distilgpt2"
    output_dir: str = str(MODULE_ROOT / "outputs")
    adapter_name: str = "lora_adapter"

    # Data
    dataset_path: str = str(MODULE_ROOT / "data" / "sample_dataset.jsonl")

    # Training hyperparameters
    num_epochs: int = 3
    batch_size: int = 2
    learning_rate: float = 2e-4
    max_seq_length: int = 256
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    logging_steps: int = 5
    save_steps: int = 50

    # LoRA
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05

    # Runtime
    device: str = "auto"  # auto | cpu | cuda
    seed: int = 42

    @field_validator("output_dir", "dataset_path")
    @classmethod
    def resolve_module_path(cls, value: str) -> str:
        path = Path(value)
        return str(path if path.is_absolute() else MODULE_ROOT / path)


settings = FineTuneSettings()
