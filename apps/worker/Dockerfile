# Build context must be the repo root so uv.lock and workspace packages are reachable
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system appgroup && adduser --system --group appuser

# ── Deps: manifests + lock first for layer-cache on external packages ──
COPY pyproject.toml uv.lock ./
COPY apps/worker/pyproject.toml apps/worker/pyproject.toml
COPY packages/schemas/pyproject.toml packages/schemas/pyproject.toml
COPY packages/shared/pyproject.toml packages/shared/pyproject.toml
COPY packages/prompts/pyproject.toml packages/prompts/pyproject.toml

RUN uv sync --package worker --frozen --no-cache --no-install-workspace

# ── Source: copy then install workspace packages in one pass ──
COPY apps/worker/src/ apps/worker/src/
COPY packages/schemas/src/ packages/schemas/src/
COPY packages/shared/src/ packages/shared/src/
COPY packages/prompts/src/ packages/prompts/src/

RUN uv sync --package worker --frozen --no-cache

RUN chown -R appuser:appgroup /app
USER appuser

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/apps/worker/src"

CMD ["celery", "-A", "worker.main:celery_app", "worker", "--loglevel=info"]
