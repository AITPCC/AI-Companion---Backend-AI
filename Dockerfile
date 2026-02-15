# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Install uv (copy from official image)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency manifests first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies with uv (no dev dependencies, no editable install)
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY . .

# Install the project in the environment
RUN uv sync --frozen --no-dev

# Expose port
EXPOSE 8080

# Start FastAPI with the FastAPI CLI
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--port", "8080", "--host", "0.0.0.0"]
