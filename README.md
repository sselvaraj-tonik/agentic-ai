# Agentic AI Banking Assistant

A production-grade, open-source AI agent for banking customer support, built with **FastAPI**, **LangGraph**, and **Ollama**.

## Features

*   **Production Ready**: Built with FastAPI for high performance.
*   **Local Privacy**: Uses Ollama to run LLMs (like Llama 3) locally on your machine.
*   **Agentic Workflow**: Uses LangGraph for stateful, multi-step reasoning.
*   **Vector Search**: Uses PostgreSQL + pgvector for FAQ knowledge base retrieval.
*   **Containerized**: Includes Docker support.

## Prerequisites

1.  **Python 3.12+**
2.  **Ollama**: [Download and Install Ollama](https://ollama.com/).
    *   **Crucial Step**: You must start the Ollama server and download a model.
    *   Run this in a separate terminal:
        ```bash
        ollama serve
        ```
    *   Then pull the required models:
        ```bash
        ollama pull llama3.1
        ollama pull nomic-embed-text
        ```
    *   > **Performance Tip**: `llama3.1` is a large model (4.9GB) and runs slowly on CPU. For faster responses, use the smaller `llama3.2:3b` model by setting `OLLAMA_MODEL=llama3.2:3b` in your `.env` file.

3.  **PostgreSQL with pgvector extension** *(required for FAQ knowledge base)*
    See the [PostgreSQL Setup](#postgresql-setup) section below.

---

## PostgreSQL Setup

The application uses **PostgreSQL** with the **pgvector** extension to store and search embedded FAQ documents. You must have a running PostgreSQL instance before starting the app.

### Option A: Docker (Recommended — easiest setup)

> **Prerequisite**: [Docker Desktop](https://www.docker.com/products/docker-desktop/) must be installed and running.

**1. Start Docker Desktop** from the Start Menu and wait for it to show a running (green) status.

**2. Pull and run the official pgvector image:**
```bash
docker run --name pgvector \
  -e POSTGRES_USER=suriya \
  -e POSTGRES_PASSWORD=123 \
  -e POSTGRES_DB=postgres \
  -p 5432:5432 \
  -d pgvector/pgvector:pg16
```

**3. Verify the container is running:**
```bash
docker ps
```
You should see `pgvector` listed with status `Up`.

**4. On subsequent runs**, just start the existing container — do NOT run `docker run` again or it will error saying the container already exists:
```bash
docker start pgvector
```

**5. To stop the database:**
```bash
docker stop pgvector
```

---

### Option B: Native Windows Installation

**1. Download** the PostgreSQL installer for Windows from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/).

**2. Run the installer** and follow the setup wizard. Note the port (default: `5432`) and the password you set for the `postgres` superuser.

**3. Create the application user and database** using `psql`:
```sql
CREATE USER suriya WITH PASSWORD '123';
CREATE DATABASE postgres OWNER suriya;
GRANT ALL PRIVILEGES ON DATABASE postgres TO suriya;
```

**4. Install the pgvector extension:**

Download and install pgvector for Windows from [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector/releases), then enable it inside psql:
```sql
\c postgres
CREATE EXTENSION IF NOT EXISTS vector;
```

**5. Start/Stop PostgreSQL service** via Windows Services (`Win + R` → `services.msc`), then find and start `postgresql-x64-16` (or your installed version).

---

### Verifying the Database is Ready

After starting PostgreSQL (via Docker or native), verify it is accessible before starting the application:

```bash
# Check port 5432 is listening (PowerShell)
Test-NetConnection -ComputerName localhost -Port 5432

# Or using psql directly
psql -U suriya -d postgres -c "SELECT version();"
```

Expected output from `Test-NetConnection`:
```
TcpTestSucceeded : True
```

---

### Database Configuration (`.env`)

The `DATABASE_URL` in your `.env` file must match your PostgreSQL credentials:

```env
# Format: postgresql+psycopg://<user>:<password>@<host>:<port>/<dbname>
DATABASE_URL=postgresql+psycopg://suriya:123@localhost:5432/postgres
```

> **Note**: The application uses `psycopg` (v3). If you see a driver error, ensure it is installed:
> ```bash
> pip install psycopg[binary]
> ```

---

### Ingesting the FAQ Knowledge Base

After the database is running and the application has started, populate it with FAQ data by calling the ingest endpoint once:

```bash
curl -X POST http://localhost:8000/ingest/faqs
```

This will fetch FAQs from the configured Drupal CMS URL, chunk them, embed them via Ollama (`nomic-embed-text`), and store them in PostgreSQL. You only need to do this once (or when the FAQ content changes).

---

## Running Locally

1.  **Clone the repository** (if you haven't already).

2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv env
    # Windows
    env\Scripts\activate
    # macOS / Linux
    source env/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables** — copy `.env.example` to `.env` and fill in your values:
    ```bash
    copy .env.example .env
    ```

5.  **Ensure all prerequisites are running**:
    *   Ollama is running (`ollama serve` or the Ollama desktop app)
    *   PostgreSQL is running (`docker start pgvector` or via Windows Services)

6.  **Start the Application**:
    ```bash
    uvicorn app.server.main:app --reload
    ```
    The API and chat UI will be available at `http://localhost:8000`.

7.  **Test the Agent** via the chat UI at `http://localhost:8000` or with curl:
    ```bash
    curl --location 'http://localhost:8000/chat' --form 'query="Get profile for 631234567890"'
    ```

---

## Running with Docker

1.  **Build the Image**:
    ```bash
    docker build -t banking-agent .
    ```

2.  **Run the Container**:
    *   *Note*: To allow the container to access your local Ollama instance, use `--network="host"` (Linux) or `host.docker.internal` (Mac/Windows).

    ```bash
    docker run -p 8000:8000 -e OLLAMA_BASE_URL="http://host.docker.internal:11434" banking-agent
    ```

---

## Troubleshooting

### App hangs / freezes at startup with no logs printed

This is caused by the database connection blocking the startup. The most likely cause is that **PostgreSQL is not running**.

**Fix:**
1.  Start PostgreSQL: `docker start pgvector` (if using Docker).
2.  Verify the port is open:
    ```powershell
    Test-NetConnection -ComputerName localhost -Port 5432
    ```

---

### `[WinError 10061] No connection could be made...` or `httpx.ConnectError`

This means the application cannot connect to Ollama.

**Fix:**
1.  Make sure **Ollama is installed**.
2.  Make sure **Ollama is running**. Open your terminal and type:
    ```bash
    curl http://localhost:11434
    ```
    It should say "Ollama is running".
3.  If it's not running, start it by opening the Ollama application or running `ollama serve`.

---

### `Connection refused` on port `5432`

**Fix:**
*   **Docker**: Run `docker ps -a` to check if the container exists, then `docker start pgvector`.
*   **Native Windows**: Open `services.msc`, find `PostgreSQL`, and click **Start**.

---

### `LangChainDeprecationWarning: OllamaEmbeddings`

**Fix:** Run the following to upgrade to the latest package:
```bash
pip install -U langchain-ollama
```

---

### Slow API responses (responses taking 2–10 minutes)

This happens when the LLM runs on **CPU** instead of GPU. Each request makes 2–3 LLM calls through the supervisor and agent nodes.

**Fix — switch to a smaller model in `.env`:**
```env
OLLAMA_MODEL=llama3.2:3b
```
Then pull the model: `ollama pull llama3.2:3b`

---

### `Input should be a valid dictionary...`

This means you sent JSON data but the API expected Form Data (or vice versa).
*   **Correct Usage**: `curl ... --form 'query="Hi"'`