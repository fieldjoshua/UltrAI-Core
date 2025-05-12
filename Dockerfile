FROM python:3.10-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    ULTRA_VERSION=1.0.0 \
    TZ=UTC

# Create a non-root user
RUN addgroup --system app && \
    adduser --system --ingroup app app

# Set work directory
WORKDIR /app

# Install dependencies
FROM base as dependencies

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https \
    build-essential \
    ca-certificates \
    cmake \
    curl \
    git \
    gnupg2 \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install dependencies in layers for better caching
COPY requirements.txt requirements-core.txt* requirements-optional.txt* ./
ENV CMAKE_ARGS="-DLLAMA_F16C=OFF"
RUN --mount=type=cache,target=/root/.cache/pip \
    if [ -f requirements-core.txt ]; then \
        pip install --no-cache-dir -r requirements-core.txt; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# Install optional dependencies if present
RUN --mount=type=cache,target=/root/.cache/pip \
    if [ -f requirements-optional.txt ]; then \
        pip install --no-cache-dir -r requirements-optional.txt || true; \
    fi

# Copy the application code
FROM dependencies as final

# Create necessary directories
RUN mkdir -p /app/logs /app/document_storage /app/temp_uploads /app/temp

# Copy application code
COPY backend /app/backend
COPY alembic.ini /app/alembic.ini
COPY gunicorn_conf.py /app/gunicorn_conf.py
COPY scripts /app/scripts

# Make scripts executable
RUN chmod +x /app/scripts/*.sh

# Change ownership to the non-root user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose application port
EXPOSE 8000

# Set volumes for persistent data
VOLUME ["/app/logs", "/app/document_storage"]

# Set healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/api/health || exit 1

# Add metadata
LABEL maintainer="Ultra AI Team" \
      version="${ULTRA_VERSION}" \
      description="Ultra AI Orchestrator for LLM Integration"

# Run the application with gunicorn
CMD ["gunicorn", "--config", "gunicorn_conf.py", "backend.app:app"]