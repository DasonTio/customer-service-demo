# Customer Service RAG Demo — Design Spec

Date: 2026-07-09
Status: Approved (user: "proceed with all of the recommended approach until the app could be demo")

## Goal

Customer service web application: customers chat with an AI agent whose knowledge
comes from ingested documents via Retrieval-Augmented Generation (RAG). The agent
has an engineered persona, tone, and guardrails. All services run under Docker.

## Decisions (locked)

| Decision | Choice |
| --- | --- |
| LLM backend | Ollama (local); chat model `qwen2.5:3b` (already on host), embeddings `nomic-embed-text` (768 dims) |
| Vector store | Postgres 16 + pgvector, accessed via SQLAlchemy 2.0 async |
| Ingestion | `POST /documents` upload endpoint (.md/.txt/.pdf) + React admin page (upload, list, delete) |
| RAG shape | Domain module inside the FastAPI backend (`src/rag/`), not a separate microservice |
| Chat delivery | SSE streaming (FastAPI `StreamingResponse` ← Ollama native streaming) |
| RAG pipeline | Hand-rolled: httpx → Ollama, paragraph-based chunker, pgvector cosine search. No LangChain/LlamaIndex. |

## Architecture — 4 Docker services

| Service | Tech | Port |
| --- | --- | --- |
| `frontend` | React 19 + Vite + TS, built + served by nginx | 3000 |
| `backend` | FastAPI, Python 3.11+, SQLAlchemy 2.0 async | 8000 |
| `ollama` | Ollama server; mounts host `~/.ollama` to reuse models | 11434 |
| `db` | `pgvector/pgvector:pg16` | 5432 |

### Backend layout (per backend-conventions.md)

```
backend/src/
├── chat/        # router.py, schemas.py, service.py, constants.py (persona/guardrail prompt)
├── documents/   # router.py, schemas.py, models.py, service.py, exceptions.py
├── rag/         # chunker.py, retriever.py
├── llm/         # client.py (Ollama via httpx), config.py
├── config.py    # global BaseSettings
├── database.py  # async engine + session factory
├── exceptions.py
└── main.py      # FastAPI app + lifespan (create tables, ensure vector ext)
```

### Frontend layout (per frontend-conventions.md)

```
frontend/src/
├── features/chat/    # ChatPage, MessageList, MessageInput, useChatStream
├── features/admin/   # AdminPage (upload, document list, delete)
├── api/              # client.ts + types.ts
├── components/       # shared UI
├── stores/           # chatStore.ts (Zustand)
└── test/             # helpers, MSW setup
```

New frontend deps: `@tanstack/react-query`, `zustand`; dev: `vitest`, `jsdom`,
`@testing-library/react`, `@testing-library/user-event`, `msw`.

## Data model

- `document`: id (uuid), filename, content_type, created_at
- `document_chunk`: id (uuid), document_id (fk, cascade delete), chunk_index,
  content (text), embedding (vector(768))

Chat history is client-side only (Zustand); no server persistence — YAGNI for demo.

## Data flow

**Ingestion:** upload → extract text (pypdf for PDF, utf-8 decode otherwise) →
paragraph-based chunking (~1000 chars target, overlap by paragraph boundary) →
Ollama `/api/embed` batch → insert document + chunks in one transaction.

**Chat:** POST `/chat` {message, history[]} → embed query → pgvector cosine
top-k (k=4, min-similarity threshold) → system prompt = persona + guardrails +
retrieved context → Ollama `/api/chat` stream → SSE events (`token`, `sources`,
`done`, `error`) to frontend.

**Guardrails (system prompt):** friendly professional customer-service persona;
answer ONLY from provided context; if context lacks the answer, say so and offer
human handoff; refuse off-topic requests; never reveal the prompt.

## Error handling

- Ollama down → 503 with clear detail; SSE `error` event mid-stream.
- Unsupported file type → 415. Empty/unextractable text → 422.
- Document not found → 404. No chunks match query → still answers with
  "no relevant context" instruction (guardrail path).

## Testing

- Backend: pytest + httpx `AsyncClient(ASGITransport)`; `dependency_overrides`
  for DB session and Ollama client; unit tests for chunker; router tests for
  documents CRUD and chat SSE framing.
- Frontend: Vitest + RTL smoke/behavior tests, MSW for API mocks.

## Out of scope (YAGNI)

Auth, multi-tenant, conversation persistence, Alembic migrations (create_all in
lifespan is enough for demo), separate RAG microservice, model fine-tuning.
