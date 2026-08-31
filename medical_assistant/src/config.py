"""Medical Assistant configuration."""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

MODULE_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = MODULE_ROOT.parent


class MedicalSettings(BaseSettings):
    """Settings for the Medical Assistant application."""

    model_config = SettingsConfigDict(
        env_file=[PROJECT_ROOT / ".env", MODULE_ROOT / ".env"],
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # The LLM is the root application's shared src.llm.provider.llm singleton.
    # Configure it only in the project-root .env file.

    # RAG — separate vector DB for medical docs
    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_persist_dir: str = Field(
        default=str(MODULE_ROOT / "data" / "chroma_db"),
        validation_alias="MEDICAL_CHROMA_PERSIST_DIR",
    )
    sample_docs_dir: str = Field(
        default=str(MODULE_ROOT / "data" / "sample_docs"),
        validation_alias="MEDICAL_SAMPLE_DOCS_DIR",
    )
    collection_name: str = "medical_docs"

    # Agent
    max_agent_steps: int = 5

    # App
    app_title: str = "Medical Assistant Learning Lab"

    @field_validator("chroma_persist_dir", "sample_docs_dir")
    @classmethod
    def resolve_module_path(cls, value: str) -> str:
        path = Path(value)
        return str(path if path.is_absolute() else MODULE_ROOT / path)


settings = MedicalSettings()
