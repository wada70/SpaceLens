from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Confluence
    confluence_url: str = "https://your-confluence.example.com"
    confluence_username: str = ""
    confluence_api_token: str = ""
    confluence_space_keys: list[str] = []  # empty = search all spaces

    # LLM (Anthropic Claude)
    anthropic_api_key: str = ""
    llm_model: str = "claude-haiku-4-5-20251001"
    llm_max_tokens: int = 512

    # Re-ranker
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_top_k: int = 5          # pages kept after re-ranking
    search_max_results: int = 20     # results fetched from Confluence before re-rank

    # App
    app_title: str = "SpaceLens"
    app_description: str = "AI-powered semantic search for Confluence"
    cors_origins: list[str] = ["*"]
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
