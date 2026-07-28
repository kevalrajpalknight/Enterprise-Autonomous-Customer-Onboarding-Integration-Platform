# apps/api/Dockerfile
FROM python:3.12-slim

# Pull the official uv binary directly
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install system runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN addgroup --system appgroup && adduser --system --group appuser

# Copy dependency files first to leverage Docker layer caching
COPY pyproject.toml uv.lock ./

# Sync dependencies using uv (creates /app/.venv by default)
RUN uv sync --frozen --no-cache

# Copy the rest of the application code
COPY . .

# Transfer ownership to the non-root user
RUN chown -R appuser:appgroup /app

USER appuser

# Add the uv virtual environment to the PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Container health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
