# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Development server (auto-reload)
uvicorn main:app --reload

# Full stack (API + Redis) via Docker
docker-compose up --build

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

Copy `.env.example` to `.env`. Minimum to run: set `LLM_PROVIDER=groq`, `LLM_MODEL=llama-3.1-8b-instant`, `GROQ_API_KEY` (free at console.groq.com), `EMBEDDING_PROVIDER=huggingface`, `EMBEDDING_MODEL=all-MiniLM-L6-v2`.

## Architecture

This is a **RAG-augmented stateful chatbot** backend. All AI logic is orchestrated through a LangGraph state machine, not directly in the service layer.

### Request lifecycle — Chat (`POST /api/chat`)

```
HTTP request (X-User-ID header, {q: "..."})
  → chat_controller.py
  → chat_service.py  →  LangGraph state machine
       ┌──────────────────────────────────┐
       │ 1. load_memory      (Redis)      │
       │ 2. retrieve_context (ChromaDB)   │
       │ 3. generate_answer  (LLM)        │
       │ 4. summarize        (LLM)        │
       │ 5. store_memory     (Redis)      │
       └──────────────────────────────────┘
  → last AIMessage content returned as response
```

### Request lifecycle — Ingest (`POST /api/ingest`)

```
{file_name, s3_url}  →  ingest_controller.py  →  ingest_service.py
  → policies.py: download PDF → SHA-256 dedup check (Redis set)
    → chunk (300 chars, 50 overlap) → embed → store in ChromaDB
```

### Key modules

| Path | Role |
|------|------|
| `graph/builder.py` | Compiles the LangGraph DAG |
| `graph/state.py` | `State` TypedDict: `user_id`, `question`, `messages`, `docs`, `summary` |
| `graph/nodes/` | One file per node (load_memory, retrieve_context, generate_answer, summarize, store_memory) |
| `utils/llm_adapter.py` | Factory: returns `ChatOpenAI` / `ChatAnthropic` / `ChatGroq` based on `LLM_PROVIDER` |
| `utils/embedding_adapter.py` | Factory: returns `OpenAIEmbeddings` / `HuggingFaceEmbeddings` based on `EMBEDDING_PROVIDER` |
| `db/redis_client.py` | Singleton Redis connection |
| `db/vector.py` | Singleton ChromaDB connection — uses `chromadb.PersistentClient` explicitly (required for ChromaDB 1.x compatibility) |
| `main.py` | App entry point — mounts `StaticFiles` at `/` after API routers so `/api/*` takes priority |
| `static/index.html` | Frontend UI — two-panel (ingest + chat), pure HTML/JS, served by FastAPI |
| `config.py` | Pydantic `Settings` — all config read from `.env` |

### Memory strategy

- **Short-term**: last 6 messages kept in `messages` list
- **Long-term**: rolling summary stored alongside messages in Redis
- **Expiry**: TTL-based (default 24 h, `REDIS_TTL_SECONDS`)
- **Per-user key**: `user_id` from `X-User-ID` header (default: `"anonymous"`)

### Multi-provider config

Switch LLM or embedding backend entirely via `.env`:

```
LLM_PROVIDER=openai | anthropic | groq
LLM_MODEL=gpt-4o-mini | claude-3-5-sonnet-20241022 | llama-3.1-8b-instant

EMBEDDING_PROVIDER=openai | huggingface
EMBEDDING_MODEL=text-embedding-3-small | all-MiniLM-L6-v2
```

## CI/CD

Two separate workflow files, CD auto-triggers when CI completes successfully.

```
.github/workflows/ci.yml   — manual trigger (workflow_dispatch)
  Install deps → docker build → push to Docker Hub (pawarmahesh2511/chatbot-app:<sha>)
        ↓  workflow_run: completed (auto)
.github/workflows/cd.yml
  SSH to EC2 → copy docker-compose.yml → generate .env
  → docker pull <sha> → docker-compose down/up → health check
```

### Required GitHub Secrets

| Secret | Value |
|--------|-------|
| `EC2_HOST` | EC2 public IP or hostname |
| `EC2_USERNAME` | SSH user (`ec2-user` or `ubuntu`) |
| `EC2_SSH_KEY` | PEM private key contents |
| `DOCKERHUB_USERNAME` | `pawarmahesh2511` |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `LLM_PROVIDER` | `groq` |
| `LLM_MODEL` | `llama-3.1-8b-instant` |
| `GROQ_API_KEY` | Groq API key (free at console.groq.com) |
| `EMBEDDING_PROVIDER` | `huggingface` |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` |
| `REDIS_PASSWORD` | Leave blank (Redis has no password) |

See [CI_CD.md](CI_CD.md) for full setup guide and troubleshooting.
