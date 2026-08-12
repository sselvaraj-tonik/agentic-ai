# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /code

# Install system dependencies
# curl is useful for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and bundled frontend into the container at /code
COPY app/ ./app/
COPY chat-screen/ ./chat-screen/

# Expose port 8000
EXPOSE 8000

# Define environment variable for OLLAMA (can be overridden at runtime)
# host.docker.internal allows access to the host machine's localhost (for Ollama) on some systems
# On Linux, usually need --network="host" or special IP.
# We'll default to a generic value that users can override.
ENV OLLAMA_BASE_URL="http://host.docker.internal:11434"
ENV OLLAMA_MODEL="llama3"

# Run uvicorn
CMD ["uvicorn", "app.server.main:app", "--host", "0.0.0.0", "--port", "8000"]
