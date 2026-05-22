
# AI Chatbot Backend Service

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![LangChain](https://img.shields.io/badge/LangChain-LLM%20Orchestration-orange)
![ChromaDB](https://img.shields.io/badge/VectorDB-Chroma-purple)

## Project Overview

A production-ready AI chatbot backend built with:

- **LangGraph** for conversation orchestration
- **RAG pipeline** using ChromaDB
- **Multi-LLM support** — OpenAI, Anthropic, Groq
- **FastAPI** for the HTTP layer
- **Redis** for short and long-term memory

Supports conversational memory, document-based Q&A, multilingual responses (Arabic / English), and scalable modular design.

## Architecture

```
User Query
   ↓
FastAPI (/api/chat)
   ↓
LangGraph Orchestrator
   ├── Load Memory      (Redis)
   ├── Retrieve Context (ChromaDB)
   ├── Generate Answer  (LLM)
   ├── Summarize
   └── Store Memory     (Redis)
   ↓
Response to User
```

## Setup

### 1. Install Miniconda

```bash
bash ~/Downloads/Miniconda3-*.sh
source ~/miniconda3/bin/activate
```

### 2. Create Environment

```bash
conda create -n chat-bot python=3.10
conda activate chat-bot
```

### 3. Clone and Install

```bash
git clone https://github.com/hasandeveloper/chat-bot.git
cd chat-bot
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Key variables:

```env
OPENAI_API_KEY=your_key_here

LLM_PROVIDER=openai          # openai | anthropic | groq
LLM_MODEL=gpt-4o-mini

EMBEDDING_PROVIDER=openai    # openai | huggingface
EMBEDDING_MODEL=text-embedding-3-small

REDIS_HOST=localhost
REDIS_PORT=6379
```

See [.env.example](.env.example) for the full list.

### 5. Run Server

```bash
uvicorn main:app --reload
```

Server runs at `http://127.0.0.1:8000`

---

Or run everything with Docker:

```bash
docker-compose up --build
```

## API

### Health Check

```
GET /health
```

### Document Ingestion

```bash
curl -X POST "http://127.0.0.1:8000/api/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "terms_conditions",
    "s3_url": "https://your-bucket.s3.amazonaws.com/terms.pdf"
  }'
```

### Chat

```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user_123" \
  -d '{"q": "what is the return policy?"}'
```

`X-User-ID` identifies the user session — memory is stored and loaded per user. Defaults to `anonymous` if omitted.

## 🧩 TODO (Roadmap)
* [ ] Evaluation 
* [ ] Dockerization

- Conversational memory (short + long-term via Redis)
- RAG-based document retrieval (ChromaDB)
- Multi-LLM provider support (OpenAI, Anthropic, Groq)
- Multilingual responses — Arabic and English, detected automatically
- LangGraph workflow orchestration
- Dockerized with Redis included
- Structured logging, CORS, input validation

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| Orchestration | LangGraph |
| LLM | OpenAI / Anthropic / Groq |
| Framework | LangChain |
| Vector DB | ChromaDB |
| Memory | Redis |
| Runtime | Python 3.10 |
| Container | Docker + Docker Compose |

## Roadmap

- [ ] Observability (LangSmith / tracing)
- [ ] Evaluation framework