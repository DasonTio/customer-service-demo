from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LLM_", env_file=".env", extra="ignore")

    GEMINI_API_KEY: str = ""
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com"
    CHAT_MODEL: str = "gemini-flash-latest"
    EMBED_MODEL: str = "gemini-embedding-2"
    # Fixed so it matches the pgvector column width (see documents/models.py).
    EMBED_DIM: int = 768
    REQUEST_TIMEOUT_SECONDS: float = 60.0


llm_settings = LLMConfig()
