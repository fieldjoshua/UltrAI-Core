FROM python:3.10-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Create a non-root user
RUN addgroup --system app && \
    adduser --system --ingroup app app

# Set work directory
WORKDIR /app

# Install dependencies
FROM base as dependencies

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    cmake \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
# Set CMAKE_ARGS to disable F16C optimization before installing requirements
# This might help with llama_cpp_python build issues on some architectures
ENV CMAKE_ARGS="-DLLAMA_F16C=OFF"
RUN pip install --no-cache-dir -r requirements.txt
# Unset CMAKE_ARGS after install if needed, though likely harmless to leave
# ENV CMAKE_ARGS=""

# Copy the application code
FROM dependencies as final

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

# Set healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/api/health || exit 1

# Run the application with gunicorn
CMD ["gunicorn", "--config", "gunicorn_conf.py", "backend.app:app"]