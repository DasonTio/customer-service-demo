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

## Deployed (live)

| Piece    | Host                                                        | URL |
| -------- | ------------------------------------------------------------ | --- |
| Database | [Neon](https://neon.tech) — Postgres + pgvector, free tier   | project `rough-fog-97471660` |
| Backend  | [Render](https://render.com) — free web service (Docker)     | https://customer-service-backend-a3ao.onrender.com |
| Frontend | [Render](https://render.com) — free static site               | https://customer-service-frontend-c95u.onrender.com |
| LLM      | [Gemini API](https://aistudio.google.com/apikey) — free tier | `gemini-flash-latest` + `gemini-embedding-2` |

Provisioned via the Neon API, Render CLI/API, and `render.yaml`. Both Render
services auto-deploy on every push to `main`.

**Limits of the free tier:** Render's free web service sleeps after 15 min
idle (cold start on wake, ~30–50s); Gemini's free tier caps requests per
minute — fine for a demo, not for production traffic.

### Redeploying elsewhere / from scratch

1. **Database — Neon.** Sign up at neon.tech, create a project, copy the
   connection string. **Rewrite it for asyncpg** — SQLAlchemy's asyncpg driver
   doesn't understand `sslmode`, only `ssl`:
   `postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require` becomes
   `postgresql+asyncpg://user:pass@ep-xxx.neon.tech/dbname?ssl=require`.
   pgvector ships preinstalled; the backend runs
   `CREATE EXTENSION IF NOT EXISTS vector` on startup.
2. **Backend — Render.** New → Blueprint → this repo (`render.yaml` is
   auto-detected), or New → Web Service manually, root directory `backend`,
   runtime Docker. Set `DATABASE_URL`, `LLM_GEMINI_API_KEY`, and
   `CORS_ORIGINS` in the dashboard (left blank in `render.yaml` on purpose so
   secrets never touch the repo). **Env var changes via the API don't
   auto-redeploy a running service** — trigger a manual deploy after changing
   them, whether via dashboard or `render deploys create <service-id>`.
3. **Frontend — Render Static Site** (or Cloudflare Pages / Vercel / Netlify,
   any static host works). Root directory `frontend`, build command
   `npm install && npm run build`, publish directory `dist`, env var
   `VITE_API_URL` = your backend URL from step 2.
4. Update the backend's `CORS_ORIGINS` to the frontend's real URL and
   redeploy.

### Verify

Open the frontend URL, upload `knowledge/acme-faq.md` on **Knowledge base**,
ask a question on **Chat**.

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

## Security note

Provisioning this deployment used personal API keys (Neon, Render) with
broad account access — treat those like passwords, not like the app's
`LLM_GEMINI_API_KEY`. If they were ever shared outside a private channel,
rotate them from each provider's dashboard.
