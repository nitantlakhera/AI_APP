"""Application configuration loaded from environment variables."""

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Central config for the AI Learning Lab."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    llm_provider: str = "ollama"  # "ollama" | "openai" | "demo"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # RAG
    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_persist_dir: str = str(PROJECT_ROOT / "data" / "chroma_db")
    sample_docs_dir: str = str(PROJECT_ROOT / "data" / "sample_docs")

    # Open Wiki (LLM Wiki pattern — alternative to RAG)
    wiki_pages_dir: str = str(PROJECT_ROOT / "data" / "wiki" / "pages")
    wiki_raw_dir: str = str(PROJECT_ROOT / "data" / "wiki" / "raw")

    # Agent
    max_agent_steps: int = 5

    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, value: str) -> str:
        provider = value.strip().lower()
        if provider not in {"demo", "ollama", "openai"}:
            raise ValueError("LLM_PROVIDER must be one of: demo, ollama, openai")
        return provider

    @field_validator("max_agent_steps")
    @classmethod
    def validate_max_agent_steps(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("MAX_AGENT_STEPS must be greater than zero")
        return value

    @field_validator("chroma_persist_dir", "sample_docs_dir", "wiki_pages_dir", "wiki_raw_dir")
    @classmethod
    def resolve_project_path(cls, value: str) -> str:
        path = Path(value)
        return str(path if path.is_absolute() else PROJECT_ROOT / path)


settings = Settings()
