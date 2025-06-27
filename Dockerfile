FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create directory structure
RUN mkdir -p /app/static/css /app/static/js /app/templates /app/tools

# Copy patching modules first
COPY sqlite3_patch.py app_wrapper.py ./

# Copy your application code
COPY *.py ./
COPY tools/ ./tools/

# Copy static and template files
COPY static/css/ ./static/css/
COPY static/js/ ./static/js/
COPY templates/ ./templates/

# Install core dependencies
RUN pip install --no-cache-dir numpy==1.24.3
RUN pip install --no-cache-dir pysqlite3-binary
RUN pip install --no-cache-dir flask==3.0.3 gunicorn==21.2.0

# Install project dependencies
RUN pip install --no-cache-dir \
    psycopg2-binary==2.9.10 \
    python-decouple==3.8 \
    boto3==1.33.6 \
    requests==2.32.4 \
    httpx==0.28.1 \
    asyncpg==0.30.0 \
    python-dotenv==1.1.0 \
    websocket-client==1.8.0 \
    email-validator==2.2.0 \
    sseclient-py==1.8.0 \
    json-repair \
    mcp==1.9.4 \
    fastmcp==2.8.1

# Install additional dependencies
RUN pip install --no-cache-dir \
    instructor \
    jinja2 \
    attrs \
    jsonpointer \
    dataclasses-json

# Install OpenTelemetry and its dependencies
RUN pip install --no-cache-dir \
    opentelemetry-api==1.21.0 \
    opentelemetry-sdk==1.21.0 \
    opentelemetry-exporter-otlp==1.21.0 \
    opentelemetry-proto==1.21.0 \
    protobuf==4.24.4

# Install CrewAI dependencies
RUN pip install --no-cache-dir \
    appdirs==1.4.4 \
    litellm \
    grpcio==1.59.3 \
    grpcio-tools==1.59.3

# Install minimal ChromaDB with dependencies
RUN pip install --no-cache-dir \
    hnswlib==0.8.0 \
    mmh3==4.0.1 \
    posthog==3.4.1 \
    chromadb==0.6.3

# Install LangChain dependencies
RUN pip install --no-cache-dir typing-inspect typing-extensions
RUN pip install --no-cache-dir pydantic==2.7.4 pydantic-settings==2.4.0
RUN pip install --no-cache-dir tenacity==9.1.2 PyYAML==6.0.2

# Install LangChain
RUN pip install --no-cache-dir \
    langchain==0.3.25 \
    langchain-core==0.3.65 \
    langchain-community==0.3.25 \
    langchain-google-genai==2.1.5 \
    google-ai-generativelanguage==0.6.18 \
    langchain-groq==0.3.2 \
    openai==1.88.0

# Install CrewAI
RUN pip install --no-cache-dir \
    crewai==0.130.0 \
    crewai-tools==0.47.1

# Set environment variable to disable telemetry
ENV CREWAI_DISABLE_TELEMETRY=true
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Start with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app_wrapper:app", "--workers", "1", "--timeout", "300"]