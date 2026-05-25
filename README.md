
# 🤖 AI Chatbot Backend Service (LangChain + LangGraph + RAG + FastAPI)

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![LangChain](https://img.shields.io/badge/LangChain-LLM%20Orchestration-orange)
![ChromaDB](https://img.shields.io/badge/VectorDB-Chroma-purple)
![LLM](https://img.shields.io/badge/LLM-OpenAI%20%7C%20Anthropic%20%7C%20Groq-black)

## 📌 Project Overview

This project is a **production-style AI chatbot backend** built using:

* 🧠 LangGraph for conversation orchestration
* 🔍 RAG pipeline using ChromaDB
* 💬 Multi-LLM support (OpenAI, Anthropic, Groq)
* ⚡ FastAPI for backend APIs
* 🧠 Redis for memory storage

It supports:

* Conversational memory
* Document-based Q&A (RAG)
* Strict knowledge-base-only responses — the bot refuses to answer outside ingested documents
* Multilingual responses (Arabic / English)
* Scalable backend design

## 🎯 Why This Project

Most chatbot APIs are stateless and cannot maintain long-term context.

This project solves that by combining:
- Stateful memory (Redis)
- Long-term summarization
- RAG-based knowledge retrieval
- LangGraph orchestration

Making it suitable for real-world SaaS integrations.

## 🧠 Architecture

```
User Query
   ↓
FastAPI (/api/chat)
   ↓
LangGraph Orchestrator
   ├── Load Memory (Redis)
   ├── Retrieve Context (ChromaDB)
   ├── Generate Answer (LLM)
   ├── Summarize Conversation
   └── Store Memory (Redis)
   ↓
Response to User
```

## 🧠 How It Works

1. User sends a question
2. System loads conversation history from Redis
3. Relevant documents are retrieved from ChromaDB (RAG)
4. LangGraph orchestrates the flow:
   - memory → retrieval → reasoning → response
5. LLM generates a final contextual answer
6. Conversation is updated + summarized for future use

## 🗂️ Project Structure

```
chat-bot/
├── .github/workflows/
│   ├── ci.yml            # CI pipeline (manual trigger — build & push Docker image)
│   └── cd.yml            # CD pipeline (auto after CI — deploy to AWS EC2)
├── controllers/          # Route handler logic
├── db/                   # Redis and ChromaDB clients
├── graph/
│   ├── builder.py        # LangGraph pipeline definition
│   └── nodes/            # Individual graph nodes (load_memory, retrieve_context, generate_answer, summarize, store_memory)
├── ingest/               # Document download and chunking logic
├── prompts/              # LLM prompt templates
├── schemas/              # Request/response validation (Pydantic)
├── services/             # Business logic (chat, ingest)
├── static/
│   └── index.html        # Frontend UI (chat + ingest)
├── utils/                # LLM and embedding adapters
├── main.py               # App entrypoint
├── config.py             # Settings (pydantic-settings)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 🌐 Frontend UI

A built-in chat interface is served at the root URL once the app is running.

```
http://<host>:8000
```

**Left panel — Knowledge Base**
- Enter a file name (no dots or slashes, e.g. `company-policy`)
- Paste an S3 PDF URL
- Click **Ingest PDF** — shows page and chunk count on success

**Right panel — Chat**
- Type a question and press **Enter** (Shift+Enter for new line)
- Conversation memory persists across page refreshes via `localStorage` user ID
- Click **Clear Chat** to start a fresh conversation

---

## 🚀 CI/CD Pipeline

Two separate GitHub Actions workflows — see [CI_CD.md](CI_CD.md) for the full setup guide.

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| `ci.yml` | Manual (`workflow_dispatch`) | Install deps → Docker build → push to Docker Hub |
| `cd.yml` | Auto after CI succeeds | SSH to EC2 → generate `.env` → pull image → deploy → health check |

Docker Hub: `pawarmahesh2511/chatbot-app`

---

## ⚙️ Setup Instructions

## 🧩 1. Install Miniconda

```bash
Visit:- https://www.anaconda.com/docs/getting-started/miniconda/install/mac-cli-install
bash ~/Downloads/Miniconda3-*.sh
source ~/miniconda3/bin/activate
```

## 🐍 2. Create Environment

```bash
conda create -n chat-bot python=3.10
conda activate chat-bot
```

## 📦 3. Clone and Install Dependencies

```bash
git clone https://github.com/hasandeveloper/chat-bot.git
cd chat-bot
pip install -r requirements.txt
```

## ⚠️ 4. Configure Environment Variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Key variables:

```env
# Free option — Groq (recommended for getting started)
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=your_groq_key   # free at console.groq.com

# OR paid — OpenAI
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_key

# Embeddings — free (no API key needed)
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL=all-MiniLM-L6-v2

REDIS_HOST=localhost
REDIS_PORT=6379
```

See [.env.example](.env.example) for the full list of options.

## 🚀 5. Run Server

```bash
uvicorn main:app --reload
```

📍 Server:

```
http://127.0.0.1:8000
```

Or run with Docker (includes Redis):

```bash
docker-compose up --build
```

## 📥 6. Document Ingestion (S3 → ChromaDB)

```bash
curl -X POST "http://127.0.0.1:8000/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "terms_conditions",
    "s3_url": "https://your-s3-url.pdf"
  }'
```

## 💬 7. Chat API

### Endpoint

```
POST /api/chat
```

### Request

```json
{
  "q": "what are the return policies?"
}
```

### Example

```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user_123" \
  -d '{"q":"what is return policy?"}'
```

> `X-User-ID` identifies the user session — memory is stored and loaded per user. Defaults to `anonymous` if omitted.

## 🏥 8. Health Check

```bash
curl http://127.0.0.1:8000/health
```

## 🧠 Core System Design

### 🔹 Memory System
Redis stores:
- Full conversation history
- Running conversation summary (for long-term context)
- TTL-based expiry (configurable via `REDIS_TTL_SECONDS`)

### 🔹 RAG System
ChromaDB:
- Stores embedded documents
- Retrieves top-k relevant context per query
- SHA-256 hash-based duplicate detection

### 🔹 LLM Layer
Configurable via environment variables:
- Uses conversation summary (long-term memory)
- Uses recent messages (short-term memory)
- Uses retrieved context (RAG)
- Generates final response in the user's language (Arabic / English)

## 🧠 Key Features

* ✅ Conversational memory (short + long-term)
* ✅ RAG-based retrieval system
* ✅ Multi-LLM provider support (OpenAI, Anthropic, Groq)
* ✅ Multilingual responses (Arabic / English auto-detected)
* ✅ LangGraph workflow orchestration
* ✅ Redis-based persistence with TTL
* ✅ Modular backend design
* ✅ FastAPI production API layer
* ✅ Dockerized with Docker Compose
* ✅ Structured logging + CORS + input validation

## 🧩 TODO (Roadmap)
* [ ] LLM: Handling tokenization differences, latency variations & fallback mechanisms
* [ ] Embedding/Search: Hybrid Search (semantic + keyword (BM25)), MMR — Diversity Ranking, Query Rewriting Node and Token optimization / Cost Tracking
* [ ] Ingestion: Document Incremental changes ingestion fix
* [ ] Evaluation

## ⚡ Tech Stack

* **Backend:** FastAPI
* **LLM:** OpenAI / Anthropic / Groq
* **Orchestration:** LangGraph
* **Framework:** LangChain
* **Vector DB:** ChromaDB
* **Cache / Memory:** Redis
* **Runtime:** Python 3.10
* **Container:** Docker + Docker Compose

## 📌 Summary

This project demonstrates a **real-world production architecture for AI chatbots** combining:

> RAG + Memory + LLM + Backend Engineering
