from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Literature Review Verifier Agent"
    app_version: str = "0.1.0"
    api_timeout_seconds: float = 10.0
    max_retrieval_candidates: int = 5
    default_mode: Literal["rule", "base_llm", "lora_llm"] = "rule"
    llm_backend: Literal["dummy", "hf_qwen", "lora_qwen"] = "dummy"
    llm_enabled: bool = False
    hf_model_name_or_path: str = "Qwen/Qwen3-4B-Instruct-2507"
    lora_adapter_path: Optional[str] = None
    device_map: str = "auto"
    torch_dtype: str = "auto"
    report_output_dir: Path = Field(default_factory=lambda: ROOT_DIR / "data" / "processed")
    openalex_base_url: str = "https://api.openalex.org/works"
    crossref_base_url: str = "https://api.crossref.org/works"
    semanticscholar_base_url: str = "https://api.semanticscholar.org/graph/v1/paper/search"
    user_agent: str = "literature-review-verifier/0.1.0 (local prototype)"
    export_markdown_inline: bool = True
    export_excel_to_disk: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.report_output_dir.mkdir(parents=True, exist_ok=True)
    return settings
