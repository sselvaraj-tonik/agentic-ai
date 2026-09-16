# 🏦 Agentic AI — Banking Customer Support

> A production-grade, open-source **multi-agent AI system** for banking customer support, built with **FastAPI**, **LangGraph**, and **Ollama** (or **vLLM** in production).

---

## 📋 Table of Contents

1. [Overview](#-overview)
2. [Architecture](#-architecture)
3. [Project Structure](#-project-structure)
4. [Tech Stack](#-tech-stack)
5. [Prerequisites](#-prerequisites)
6. [Environment Configuration](#-environment-configuration)
7. [Database Setup — PostgreSQL + pgvector](#-database-setup--postgresql--pgvector)
8. [Running Locally](#-running-locally)
9. [FAQ Knowledge Base](#-faq-knowledge-base)
10. [Running with Docker](#-running-with-docker)
11. [API Reference](#-api-reference)
12. [LLM Provider Configuration](#-llm-provider-configuration)
13. [Multi-Environment Support](#-multi-environment-support)
14. [Troubleshooting](#-troubleshooting)

---

## 🧭 Overview

This project is a **supervisor-driven multi-agent AI** designed for Tonik Bank's customer support. A central **Supervisor** node acts as a secure traffic router — it classifies each user request and delegates it to the correct **specialized agent** (Accounts, Loans, or Common). Each agent is independently equipped with LLM-bound tools that call real APIs or query an internal knowledge base.

**Key Capabilities:**
- 🔀 **Intelligent routing** via a hardened Supervisor that is injection-resistant
- 🏧 **Accounts Agent** — Profile lookup, payee search, fund transfers (with explicit user confirmation)
- 💳 **Loans Agent** — Loan status checks, EMI payment processing (with explicit user confirmation)
- 🤖 **Common Agent** — FAQs, greetings, product knowledge, and out-of-scope deflection
- 🔍 **Vector Search** — FAQ knowledge base stored in PostgreSQL (pgvector) with Ollama embeddings
- 🔒 **PII Masking** — Phone numbers, emails, card numbers, and account numbers masked in logs
- ♻️ **Stateful Conversations** — Thread-scoped memory via LangGraph checkpointers (in-memory or PostgreSQL)
- 🌍 **Multi-Environment** — Separate `.env` files for development, sit, uat, and production

---

## 🏗️ Architecture

```
User Request (HTTP POST /chat)
         │
         ▼
  ┌─────────────┐
  │  FastAPI    │  (Async endpoint, PII-masked logging, latency tracking)
  └──────┬──────┘
         │ LangGraph ainvoke (thread_id scoped)
         ▼
  ┌──────────────────────────────────────────────────────┐
  │                  LangGraph StateGraph                │
  │                                                      │
  │   START ──► [ Supervisor Node ]                      │
  │                     │                                │
  │        ┌────────────┼─────────────┐                  │
  │        ▼            ▼             ▼                  │
  │  [Accounts Agent] [Common Agent] [Loans Agent]        │
  │        │              │              │               │
  │        ▼              ▼              ▼               │
  │  [accounts_tools] [common_tools] [loans_tools]        │
  │  (ToolNode)       (ToolNode)     (ToolNode)           │
  │        │              │              │               │
  │        └──────────────┼──────────────┘               │
  │                    [END / FINISH]                    │
  └──────────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────┐
  │         External Integrations           │
  │  - Bank REST API  (profileinfo, etc.)   │
  │  - Drupal CMS FAQ  (JSON:API)           │
  │  - PostgreSQL + pgvector (embeddings)   │
  │  - Ollama / vLLM  (LLM inference)       │
  └─────────────────────────────────────────┘
```

### Routing Flow

1. Every request enters the **Supervisor** node first.
2. The Supervisor uses a structured LLM call (`with_structured_output`) to classify the intent and returns one of: `accounts_agent`, `common_agent`, `loans_agent`, or `FINISH`.
3. The matched agent invokes its LLM-bound tools (real API calls or vector search).
4. After tool execution, the loop returns to the agent to formulate a final response.
5. The conversation state (message history + `next_node`) is persisted per `thread_id`.

---

## 📁 Project Structure

```
agentic-ai/
│
├── app/                        # Core application package
│   ├── config/
│   │   ├── settings.py         # Pydantic BaseSettings — all env vars + enums
│   │   └── logging.py          # Custom PII-masking log formatter
│   │
│   ├── core/
│   │   ├── state.py            # AgentState (MessagesState + next_node) & RouteResponse schema
│   │   ├── llm.py              # LLM factory — returns ChatOllama or ChatOpenAI (vLLM)
│   │   ├── database.py         # PGVector store factory — Ollama or OpenAI embeddings
│   │   ├── security.py         # PII masking via regex (email, phone, card, account)
│   │   ├── decorators.py       # @log_execution_time / @async_log_execution_time
│   │   └── exceptions.py       # Custom exception types
│   │
│   ├── graph/
│   │   └── builder.py          # LangGraph StateGraph builder — nodes, edges, checkpointer
│   │
│   ├── modules/
│   │   ├── supervisor/
│   │   │   └── agent.py        # Supervisor node + route_supervisor conditional edge
│   │   │
│   │   ├── accounts/
│   │   │   ├── agent.py        # Accounts agent node (bound to tools)
│   │   │   ├── tools.py        # get_customer_profile, search_payee, execute_transfer
│   │   │   └── schemas.py      # Pydantic input/output schemas for account tools
│   │   │
│   │   ├── loans/
│   │   │   ├── agent.py        # Loans agent node (bound to tools)
│   │   │   ├── tools.py        # check_loan_status, process_loan_payment
│   │   │   └── schemas.py      # Pydantic input/output schemas for loan tools
│   │   │
│   │   └── common/
│   │       ├── agent.py        # Common agent node (bound to vector search tool)
│   │       ├── tools.py        # search_company_knowledge (pgvector similarity search)
│   │       └── schemas.py      # Pydantic input schema for knowledge search
│   │
│   └── server/
│       ├── main.py             # FastAPI app init, middleware, router mounting, /health
│       └── routers/
│           └── chat.py         # POST /chat — async graph invocation with thread_id
│
├── chat-screen/                # Bundled frontend chat UI
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── tests/
│   └── test_production_features.py   # Tests for env switching and PII masking
│
├── .env.example                # Template — copy to .env.<environment>
├── .env.development            # Local dev settings
├── .env.sit                    # SIT settings (vLLM, Postgres, PII masking ON)
├── .env.uat                    # UAT settings (vLLM, Postgres, PII masking ON)
├── .env.production             # Production settings (vLLM, PostgreSQL persistence)
├── Dockerfile                  # Python 3.12-slim image
├── requirements.txt            # All Python dependencies
└── Ollama_Commands.txt         # Quick Ollama setup reference
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **Web Framework** | [FastAPI](https://fastapi.tiangolo.com/) |
| **Agent Orchestration** | [LangGraph](https://langchain-ai.github.io/langgraph/) |
| **LLM (Local)** | [Ollama](https://ollama.com/) (`llama3.1`, `llama3.2:3b`) |
| **LLM (Production)** | [vLLM](https://docs.vllm.ai/) (OpenAI-compatible API) |
| **Embeddings** | `nomic-embed-text` via Ollama |
| **Vector Store** | PostgreSQL + [pgvector](https://github.com/pgvector/pgvector) via `langchain-postgres` |
| **State Persistence** | LangGraph `MemorySaver` (dev) / `PostgresSaver` (sit/uat/prod) |
| **Settings** | [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) (`pydantic-settings`) |
| **ASGI Server** | [Uvicorn](https://www.uvicorn.org/) |
| **FAQ Source** | Drupal CMS JSON:API (`/jsonapi/node/faq`) |
| **Containerisation** | Docker (Python 3.12-slim) |

---

## ✅ Prerequisites

Before starting, ensure the following are installed and running:

### 1. Python 3.12+

```bash
python --version   # Should show 3.12.x or higher
```

### 2. Ollama (for local/development use)

[Download Ollama →](https://ollama.com/)

Start the Ollama server and pull the required models:

```bash
ollama serve
```

```bash
# LLM for reasoning and chat
ollama pull llama3.1

# Embedding model for vector search
ollama pull nomic-embed-text
```

> **Performance tip:** `llama3.1` (4.9 GB) runs slowly on CPU. Switch to a lighter model:
> ```bash
> ollama pull llama3.2:3b
> ```
> Then set `OLLAMA_MODEL=llama3.2:3b` in your `.env.development`.

### 3. PostgreSQL with pgvector

Required for the FAQ knowledge base. See [Database Setup](#-database-setup--postgresql--pgvector) below.

---

## 🔧 Environment Configuration

The app uses **Pydantic Settings** and selects the correct `.env` file based on the `APP_ENV` environment variable.

| File | Purpose |
|---|---|
| `.env.example` | Template — copy this as your starting point |
| `.env.development` | Local dev (**Ollama**, in-memory persistence, PII masking off) |
| `.env.sit` | SIT (**vLLM**, Postgres persistence, PII masking on) |
| `.env.uat` | UAT (**vLLM**, Postgres persistence, PII masking on) |
| `.env.production` | Production (**vLLM**, Postgres persistence, PII masking on) |

> **Note:** Only `development` uses Ollama. `sit`, `uat`, and `production` all use vLLM.

### Step 1 — Create your local config

```bash
copy .env.example .env.development
```

### Step 2 — Fill in the values

```env
# ── LLM Configuration ──────────────────────────────────────
LLM_PROVIDER=ollama                         # or "vllm" for production
OLLAMA_MODEL=llama3.1                       # or llama3.2:3b for faster responses
OLLAMA_BASE_URL=http://127.0.0.1:11434

# ── vLLM (Production Only) ─────────────────────────────────
# VLLM_MODEL=llama3.1
# VLLM_BASE_URL=http://vllm-server:8000/v1
# VLLM_API_KEY=your-api-key

# ── External APIs ──────────────────────────────────────────
BANK_API_BASE_URL=https://test.alb.tonikbank.com/customer/v1/
API_TIMEOUT=10

# ── Database ───────────────────────────────────────────────
# Format: postgresql+psycopg://<user>:<password>@<host>:<port>/<dbname>
DATABASE_URL=postgresql+psycopg://suriya:123@localhost:5432/postgres

# ── Persistence ────────────────────────────────────────────
PERSISTENCE_TYPE=memory                     # "memory" (dev) or "postgres" (sit/uat/prod)

# ── Security ───────────────────────────────────────────────
ENABLE_PII_MASKING=False                    # Set True in sit/uat/prod

# ── App ────────────────────────────────────────────────────
APP_NAME="Banking Agent AI"
APP_VERSION=1.2.0
DEBUG=True
```

---

## 🗄️ Database Setup — PostgreSQL + pgvector

The app uses **PostgreSQL** with the **pgvector** extension to store and search embedded FAQ documents.

### Option A: Docker *(Recommended)*

> **Prerequisite:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) must be installed and running.

**First-time setup** — pull and start the pgvector image:

```bash
docker run --name pgvector \
  -e POSTGRES_USER=suriya \
  -e POSTGRES_PASSWORD=123 \
  -e POSTGRES_DB=postgres \
  -p 5432:5432 \
  -d pgvector/pgvector:pg16
```

**Verify the container is running:**

```bash
docker ps
# ✅ You should see "pgvector" with status "Up"
```

**Subsequent runs** — just start the existing container (do NOT re-run `docker run`):

```bash
docker start pgvector
```

**To stop:**

```bash
docker stop pgvector
```

---

### Option B: Native Windows Installation

1. Download and run the installer from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/).
2. Open `psql` and create the application user and database:

```sql
CREATE USER suriya WITH PASSWORD '123';
CREATE DATABASE postgres OWNER suriya;
GRANT ALL PRIVILEGES ON DATABASE postgres TO suriya;
```

3. Install the pgvector extension from [github.com/pgvector/pgvector/releases](https://github.com/pgvector/pgvector/releases), then enable it:

```sql
\c postgres
CREATE EXTENSION IF NOT EXISTS vector;
```

4. Start/stop the service via **Windows Services** (`Win + R` → `services.msc`) → find `postgresql-x64-16`.

---

### Verifying Database Connectivity

```powershell
# PowerShell — check port 5432
Test-NetConnection -ComputerName localhost -Port 5432
# Expected: TcpTestSucceeded : True
```

```bash
# Direct psql check
psql -U suriya -d postgres -c "SELECT version();"
```

---

## 🚀 Running Locally

```bash
# 1. Clone the repository
git clone <repo-url>
cd agentic-ai

# 2. Create and activate a virtual environment
python -m venv env

# Windows
env\Scripts\activate

# macOS / Linux
source env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment config (see Environment Configuration above)
copy .env.example .env.development

# 5. Ensure Ollama and PostgreSQL are running
ollama serve           # in a separate terminal
docker start pgvector  # if using Docker

# 6. Start the application
uvicorn app.server.main:app --reload
```

The server starts at **`http://localhost:8000`**.

| URL | Description |
|---|---|
| `http://localhost:8000` | Chat UI (served from `/chat-screen`) |
| `http://localhost:8000/health` | Health check endpoint |
| `http://localhost:8000/docs` | Swagger / OpenAPI interactive docs |
| `http://localhost:8000/redoc` | ReDoc API documentation |

---

## 📥 FAQ Knowledge Base

FAQ ingestion has been **moved out of this service** into a standalone AWS Lambda
(`agentic-ai-ingest-lambda`). That service fetches FAQs from Drupal, chunks and
embeds them, and writes to the `company_faqs` collection in PostgreSQL/pgvector.

This service is **read-only** against that collection — it queries the FAQ
vectors via `search_company_knowledge` but never writes them. Ensure the
ingestion Lambda has run (and uses the **same embedding model** configured here)
before relying on knowledge-base answers.

See the `agentic-ai-ingest-lambda` repository for deploy and scheduling details.

---

## 🐳 Running with Docker

```bash
# 1. Build the image
docker build -t banking-agent .

# 2. Run the container
#    On Mac/Windows: use host.docker.internal to reach your local Ollama
docker run -p 8000:8000 \
  -e OLLAMA_BASE_URL="http://host.docker.internal:11434" \
  -e DATABASE_URL="postgresql+psycopg://suriya:123@host.docker.internal:5432/postgres" \
  banking-agent

# On Linux: use --network="host" so the container can reach localhost
docker run --network="host" banking-agent
```

> **Note:** The Dockerfile entrypoint is `uvicorn app.server.main:app --host 0.0.0.0 --port 8000`.  
> All environment variables can be overridden with `-e` flags at runtime.

---

## 📡 API Reference

### `POST /chat`

Sends a user message to the multi-agent pipeline.

**Request** (Form Data):

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | `string` | ✅ | — | The user's message |
| `thread_id` | `string` | ❌ | `default_thread_1` | Conversation thread ID for session continuity |

**Example:**

```bash
# Basic query
curl -X POST http://localhost:8000/chat \
  --form 'query="Get profile for 631234567890"'

# With a specific conversation thread
curl -X POST http://localhost:8000/chat \
  --form 'query="What is my loan EMI?"' \
  --form 'thread_id="user_session_abc123"'
```

**Response:**

```json
{
  "response": "Here are your account details...",
  "latency_ms": 2341.7
}
```

---

### `GET /health`

Returns application health status.

```bash
curl http://localhost:8000/health
```

**Response:**

```json
{
  "status": "ok",
  "app": "Banking Agent AI",
  "version": "1.2.0"
}
```

---

## 🤖 LLM Provider Configuration

The app supports two LLM backends, switchable via the `LLM_PROVIDER` setting.

### Ollama *(Development only)*

Set in `.env.development`:

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_EMBED_MODEL=nomic-embed-text
```

**Available models (recommended):**

| Model | Size | Speed | Use Case |
|---|---|---|---|
| `llama3.1` | 4.9 GB | Slow on CPU | Best accuracy |
| `llama3.2:3b` | 2.0 GB | Fast on CPU | Development / testing |

### vLLM *(SIT / UAT / Production)*

Set in `.env.sit`, `.env.uat`, or `.env.production`:

```env
LLM_PROVIDER=vllm
VLLM_MODEL=Qwen/Qwen2.5-7B-Instruct
VLLM_BASE_URL=http://vllm-server:8000/v1
VLLM_API_KEY=your-api-key
VLLM_EMBED_MODEL=BAAI/bge-base-en-v1.5   # must be an embedding model your vLLM serves
```

> vLLM exposes an OpenAI-compatible API, so the app connects via `ChatOpenAI` internally.

---

## 🌍 Multi-Environment Support

The application auto-selects the correct `.env` file using the `APP_ENV` variable:

```
APP_ENV=development  →  loads .env.development
APP_ENV=sit          →  loads .env.sit
APP_ENV=uat          →  loads .env.uat
APP_ENV=production   →  loads .env.production
```

**To run in a specific environment:**

```powershell
# Windows PowerShell
$env:APP_ENV="uat"; uvicorn app.server.main:app --reload
```

```bash
# Linux / macOS
APP_ENV=uat uvicorn app.server.main:app --reload
```

**Environment summary:**

| Setting | Development | SIT | UAT | Production |
|---|---|---|---|---|
| `LLM_PROVIDER` | `ollama` | `vllm` | `vllm` | `vllm` |
| `PERSISTENCE_TYPE` | `memory` | `postgres` | `postgres` | `postgres` |
| `ENABLE_PII_MASKING` | `False` | `True` | `True` | `True` |
| `DEBUG` | `True` | `True` | `False` | `False` |

---

## 🔧 Troubleshooting

### App hangs / freezes at startup with no output

**Cause:** PostgreSQL is not running and the database connection is blocking startup.

**Fix:**
```bash
docker start pgvector   # if using Docker

# Verify the port is open (PowerShell)
Test-NetConnection -ComputerName localhost -Port 5432
# Expected: TcpTestSucceeded : True
```

---

### `[WinError 10061]` or `httpx.ConnectError` on startup

**Cause:** The application cannot connect to Ollama.

**Fix:**
```bash
# Check if Ollama is running
curl http://localhost:11434
# Expected: "Ollama is running"

# If not running, start it
ollama serve
```

---

### `Connection refused` on port `5432`

**Fix (Docker):**
```bash
docker ps -a                  # check if container exists
docker start pgvector         # start it
```

**Fix (Native Windows):**  
Open `services.msc` → find `PostgreSQL` → click **Start**.

---

### `LangChainDeprecationWarning: OllamaEmbeddings`

**Fix:**
```bash
pip install -U langchain-ollama
```

---

### Slow responses (2–10 minutes per request)

**Cause:** The LLM is running on CPU instead of GPU. Each request invokes 2–3 LLM calls through the supervisor and agent nodes.

**Fix — switch to a smaller model:**
```env
# In .env.development
OLLAMA_MODEL=llama3.2:3b
```
```bash
ollama pull llama3.2:3b
```

---

### `Input should be a valid dictionary` error

**Cause:** The `/chat` endpoint expects **Form Data**, not JSON.

**Correct usage:**
```bash
curl -X POST http://localhost:8000/chat --form 'query="Hello"'
```

**Incorrect usage:**
```bash
# ❌ Do NOT use -H "Content-Type: application/json" -d '{"query": "Hello"}'
```

---

## 📦 Dependencies

All packages are listed in `requirements.txt`. Key dependencies:

| Package | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `langgraph` | Multi-agent state graph orchestration |
| `langchain` | LLM tooling and abstractions |
| `langchain-ollama` | Ollama LLM + embedding integration |
| `langchain-openai` | OpenAI-compatible LLM (used for vLLM) |
| `langchain-postgres` | PGVector vector store + PostgresSaver checkpointer |
| `pydantic-settings` | Environment-based configuration |
| `psycopg[binary]` | PostgreSQL driver (psycopg v3) |
| `python-multipart` | Form data parsing for `/chat` endpoint |
| `pgvector` | pgvector Python client |
| `sqlalchemy` | ORM / DB connection layer |