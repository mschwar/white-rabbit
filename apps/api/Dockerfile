# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency metadata first for layer caching
COPY pyproject.toml uv.lock ./
COPY packages/core/pyproject.toml packages/core/uv.lock ./packages/core/

# Install dependencies (editable core package)
RUN uv sync --no-dev --frozen

# Copy application code
COPY apps/api ./apps/api
COPY packages/core/src ./packages/core/src

# Ensure local package is installed in editable mode
RUN uv pip install -e ./packages/core

ENV PYTHONPATH=/app/apps/api:/app/packages/core/src
ENV PORT=8000

EXPOSE 8000

# Run migrations on startup, then start the server
CMD ["sh", "-c", "cd /app/apps/api && uv run alembic upgrade head && uv run uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
