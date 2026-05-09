# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the entire monorepo so uv can resolve the workspace
COPY . .

# Install dependencies from the API package (which depends on core via path)
RUN cd apps/api && uv sync --no-dev --frozen

ENV PYTHONPATH=/app/apps/api:/app/packages/core/src
ENV PORT=8000

EXPOSE 8000

# Run migrations on startup, then start the server
CMD ["sh", "-c", "cd /app/apps/api && uv run alembic upgrade head && uv run uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
