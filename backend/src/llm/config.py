from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LLM_", env_file=".env", extra="ignore")

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    CHAT_MODEL: str = "qwen2.5:3b"
    EMBED_MODEL: str = "nomic-embed-text"
    EMBED_DIM: int = 768
    REQUEST_TIMEOUT_SECONDS: float = 120.0


llm_settings = LLMConfig()
