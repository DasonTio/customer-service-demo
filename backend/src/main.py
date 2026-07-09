from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.chat.router import router as chat_router
from src.config import settings
from src.database import engine
from src.documents.router import router as documents_router
from src.llm.client import OllamaClient
from src.models import Base

SHOW_DOCS_IN = {"local", "staging"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.llm = OllamaClient()
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    await app.state.llm.close()
    await engine.dispose()


app_kwargs: dict = {"title": "Customer Service RAG API", "lifespan": lifespan}
if settings.ENVIRONMENT not in SHOW_DOCS_IN:
    app_kwargs["openapi_url"] = None

app = FastAPI(**app_kwargs)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(chat_router)


@app.get("/health", tags=["health"], summary="Liveness probe")
async def health() -> dict[str, str]:
    return {"status": "ok"}
