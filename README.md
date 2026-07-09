# Customer Service RAG Demo

Customer service web app: customers chat with **Aria**, an AI agent that
answers only from your ingested knowledge base (Retrieval-Augmented
Generation), with an engineered persona and guardrails.

## Stack

| Service    | Tech                                        | Port  |
| ---------- | ------------------------------------------- | ----- |
| `frontend` | React 19 + TypeScript + Vite, nginx         | 3000  |
| `backend`  | FastAPI, SQLAlchemy 2.0 async               | 8000  |
| `ollama`   | Ollama — `qwen2.5:3b` chat, `nomic-embed-text` embeddings | 11434 |
| `db`       | Postgres 16 + pgvector                      | 5432  |

## Run the demo

```shell
docker compose up -d --build
```

First start pulls the embedding model (~274MB); the compose file mounts your
host `~/.ollama` so models you already have are reused. Override the chat
model with `CHAT_MODEL=llama3.2 docker compose up -d`.

Then:

1. Open http://localhost:3000
2. Go to **Knowledge base** → upload `knowledge/acme-faq.md` (or your own .txt/.md/.pdf)
3. Go to **Chat** → ask "What is your refund policy?"

API docs: http://localhost:8000/docs

## How RAG works here

Upload → text extraction (pypdf for PDFs) → paragraph-based chunking
(~1000 chars, 1-paragraph overlap) → Ollama embeddings → pgvector.

Chat → embed the question → cosine top-4 chunks (distance < 0.75) → system
prompt = persona + guardrails + retrieved context → Ollama streams the
answer over SSE (`sources`, `token`*, `done`).

## Development

Backend:

```shell
cd backend
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest          # tests
.venv/bin/ruff check src tests      # lint
.venv/bin/uvicorn src.main:app --reload
```

Frontend:

```shell
cd frontend
npm install
npm run dev        # http://localhost:3000
npm run test       # Vitest + RTL + MSW
npm run typecheck && npm run lint
```

Design spec: `docs/superpowers/specs/2026-07-09-customer-service-rag-design.md`
