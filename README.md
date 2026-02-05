# Agentic AI Banking Assistant

A production-grade, open-source AI agent for banking customer support, built with **FastAPI**, **LangGraph**, and **Ollama**.

## Features

*   **Production Ready**: Built with FastAPI for high performance.
*   **Local Privacy**: Uses Ollama to run LLMs (like Llama 3) locally on your machine.
*   **Agentic Workflow**: Uses LangGraph for stateful, multi-step reasoning.
*   **Containerized**: Includes Docker support.

## Prerequisites

1.  **Python 3.12+**
2.  **Ollama**: [Download and Install Ollama](https://ollama.com/).
    *   **Crucial Step**: You must start the Ollama server and download a model.
    *   Run this in a separate terminal:
        ```bash
        ollama serve
        ```
    *   Then run:
        ```bash
        ollama pull llama3
        ```

## Running Locally

1.  **Clone the repository** (if you haven't already).

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Start the Application**:
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://localhost:8000`.

4.  **Test the Agent**:
    You can use `curl` with form data:
    ```bash
    curl --location 'http://localhost:8000/chat' --form 'query="Get profile for 631234567890"'
    ```

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

## Troubleshooting

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

### `Input should be a valid dictionary...`

This means you sent JSON data but the API expected Form Data (or vice versa).
*   **Correct Usage**: `curl ... --form 'query="Hi"'`
