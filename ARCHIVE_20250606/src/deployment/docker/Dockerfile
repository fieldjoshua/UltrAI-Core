# Multi-stage build for Ultra

# ----- Frontend Build Stage -----
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend

# Copy frontend files
COPY package.json package-lock.json ./
# Install dependencies
RUN npm ci

# Copy the rest of the frontend source code
COPY src ./src
COPY public ./public
COPY index.html vite.config.js tsconfig*.json ./

# Build the frontend
RUN npm run build

# ----- Backend Dependencies Stage -----
FROM python:3.12-slim AS backend-deps
WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .
COPY .env* ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ----- Final Image -----
FROM python:3.12-slim
WORKDIR /app

# Install production system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend from backend-deps stage
COPY --from=backend-deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=backend-deps /usr/local/bin /usr/local/bin
COPY --from=backend-deps /app/backend/.env* /app/

# Copy backend source
COPY backend/ /app/backend/
COPY api.py ultra_pattern_orchestrator.py /app/

# Copy frontend build from frontend-build stage
COPY --from=frontend-build /app/frontend/dist /app/static

# Create a non-root user
RUN useradd -m ultrauser && chown -R ultrauser:ultrauser /app
USER ultrauser

# Create directories needed at runtime
RUN mkdir -p /app/backend/temp_uploads /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8085

# Expose the port the app runs on
EXPOSE 8085

# Create healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8085/api/system/health || exit 1

# Start the application
CMD ["python", "backend/main.py"]
