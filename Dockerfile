# ==========================================
# Multi-stage Dockerfile for Agentic AI
# ==========================================

# ==========================================
# Stage 1: Base Image
# ==========================================
FROM python:3.10-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ==========================================
# Stage 2: Dependencies
# ==========================================
FROM base as dependencies

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ==========================================
# Stage 3: Development
# ==========================================
FROM dependencies as development

# Copy application code
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Default command for development
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ==========================================
# Stage 4: Production
# ==========================================
FROM dependencies as production

# Create non-root user
RUN useradd -m -u 1000 agenticai && \
    chown -R agenticai:agenticai /app

# Copy application code
COPY --chown=agenticai:agenticai . .

# Set Python path
ENV PYTHONPATH=/app \
    APP_ENV=production

# Switch to non-root user
USER agenticai

# Create necessary directories
RUN mkdir -p /app/data/logs /app/data/vector_db /app/data/uploads

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command for production
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ==========================================
# Usage Examples
# ==========================================
# Development:
#   docker build --target development -t agentic-ai:dev .
#   docker run -p 8000:8000 -v $(pwd):/app agentic-ai:dev
#
# Production:
#   docker build --target production -t agentic-ai:prod .
#   docker run -p 8000:8000 agentic-ai:prod
