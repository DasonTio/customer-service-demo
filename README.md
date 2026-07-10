# Customer Service RAG Demo

Customer service web app: customers chat with **Aria**, an AI agent that
answers only from your ingested knowledge base (Retrieval-Augmented
Generation), with an engineered persona and guardrails.

## Stack

| Service    | Tech                                          | Port |
| ---------- | ---------------------------------------------- | ---- |
| `frontend` | React 19 + TypeScript + Vite, nginx             | 3000 |
| `backend`  | FastAPI, SQLAlchemy 2.0 async                   | 8000 |
| Gemini API | `gemini-flash-latest` chat, `gemini-embedding-2` embeddings | —    |
| `db`       | Postgres 16 + pgvector                          | 5432 |

## Run locally

Get a free API key at https://aistudio.google.com/apikey, then:

```shell
cp .env.example .env        # paste your GEMINI_API_KEY into .env
docker compose up -d --build
```

Then:

1. Open http://localhost:3000
2. Go to **Knowledge base** → upload `knowledge/acme-faq.md` (or your own .txt/.md/.pdf)
3. Go to **Chat** → ask "What is your refund policy?"

API docs: http://localhost:8000/docs

## How RAG works here

Upload → text extraction (pypdf for PDFs) → paragraph-based chunking
(~1000 chars, 1-paragraph overlap) → Gemini embeddings → pgvector.

Chat → embed the question → cosine top-4 chunks (distance < 0.75) → system
prompt = persona + guardrails + retrieved context → Gemini streams the
answer over SSE (`sources`, `token`*, `done`). A guardrail reminder is
appended right before generation to resist prompt-injection attempts
("ignore your instructions...") — verified against real Gemini output.

## Deploy for free

Three free-tier services, zero cost, ~15 minutes:

| Piece    | Host                                       |
| -------- | ------------------------------------------- |
| Database | [Neon](https://neon.tech) — Postgres + pgvector, free tier |
| Backend  | [Render](https://render.com) — free web service (Docker)   |
| Frontend | [Cloudflare Pages](https://pages.cloudflare.com) — free static hosting |
| LLM      | [Gemini API](https://aistudio.google.com/apikey) — free tier |

### 1. Database — Neon

1. Sign up at neon.tech (no card required), create a project.
2. Copy the connection string from the dashboard. It looks like:
   `postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require`
3. **Rewrite it for asyncpg** — SQLAlchemy's asyncpg driver doesn't understand
   `sslmode`, only `ssl`. Change the string to:
   `postgresql+asyncpg://user:pass@ep-xxx.neon.tech/dbname?ssl=require`
4. pgvector ships preinstalled on Neon. The backend runs
   `CREATE EXTENSION IF NOT EXISTS vector` on startup — nothing else to do.

### 2. Backend — Render

1. Sign up at render.com, connect your GitHub account.
2. **New → Blueprint** → select this repo (`render.yaml` is auto-detected),
   or **New → Web Service** manually with root directory `backend`, runtime Docker.
3. In the Render dashboard, set these env vars (left blank in `render.yaml`
   on purpose so secrets never touch the repo):
   - `DATABASE_URL` — the rewritten Neon string from step 1
   - `LLM_GEMINI_API_KEY` — your Gemini key
   - `CORS_ORIGINS` — `["https://your-app.pages.dev"]` (update after step 3, redeploy)
4. Deploy. Note the URL, e.g. `https://customer-service-backend.onrender.com`.
   Free tier spins down after 15 min idle — first request after that takes
   ~30–50s to cold-start.

### 3. Frontend — Cloudflare Pages

1. Sign up at dash.cloudflare.com, **Workers & Pages → Create → Pages →
   Connect to Git** → this repo.
2. Build settings: framework preset **Vite**, root directory `frontend`,
   build command `npm run build`, output directory `dist`.
3. Environment variable: `VITE_API_URL` = your Render backend URL from step 2.
4. Deploy. Note the URL, e.g. `https://customer-service-demo.pages.dev`.
5. Back in Render, update `CORS_ORIGINS` to include this URL and redeploy
   the backend.

### 4. Verify

Open your Pages URL, upload `knowledge/acme-faq.md` on **Knowledge base**,
ask a question on **Chat**.

**Limits of the free tier:** Render's free web service sleeps after 15 min
idle (cold start on wake); Gemini's free tier caps requests per minute —
fine for a demo, not for production traffic.

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
