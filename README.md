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
    *   Pull the model you want to use (default is `llama3`):
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
    Send a POST request to the chat endpoint:
    ```bash
    curl -X POST "http://localhost:8000/chat" \
         -H "Content-Type: application/json" \
         -d '{"query": "Get profile for 631234567890"}'
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

## Configuration

You can configure the application using environment variables or a `.env` file:

*   `OLLAMA_BASE_URL`: URL of the Ollama instance (default: `http://localhost:11434`).
*   `OLLAMA_MODEL`: Model to use (default: `llama3`).
*   `BANK_API_URL`: URL of the banking API.
