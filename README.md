# OnboardAI — Enterprise Autonomous Customer Onboarding Platform

Enterprise-grade platform that transforms unstructured client data (PDFs, CSVs, SQL dumps, JSON APIs) into validated, production-ready records using multimodal AI, multi-agent orchestration, human-in-the-loop review, and full observability.

---

## Why this project exists

Enterprise onboarding often takes **days or weeks** because customer data arrives in inconsistent formats, schemas evolve constantly, and validation rules are embedded in human workflows.

This project demonstrates how I would design and operate a **production-ready AI integration platform** as a **Forward Deployed Engineer (FDE)**:

- Understand ambiguous client data
- Build adaptive ingestion pipelines
- Orchestrate AI + deterministic validation
- Keep humans in control
- Deploy, monitor, and evaluate the system end-to-end

---

## FDE Lens

| Capability | Demonstrated |
|---|---|
| Client problem framing | Messy enterprise onboarding |
| Systems architecture | Multi-service platform |
| AI engineering | Vision + text extraction |
| Workflow orchestration | LangGraph |
| Backend engineering | FastAPI + Celery |
| Frontend product thinking | Next.js HITL dashboard |
| DevOps | Docker, CI/CD, AWS |
| Reliability | Retries, idempotency, DLQ |
| Governance | PII masking & audit trail |
| Evaluation | LangSmith / Phoenix metrics |

> The goal is not a demo. The goal is an operable enterprise system.

---

## Current Implementation Status

### Completed

#### API Gateway (`apps/api`)
- FastAPI application with full OpenAPI 3.1 docs (`/v1/docs`)
- JWT Bearer authentication (`python-jose`) with `get_current_user` dependency
- Redis-backed rate limiting via `fastapi-limiter` (20 req/min, configurable)
- Structured `422`/HTTP error responses with consistent JSON envelope
- CORS middleware, lifespan management, graceful shutdown

#### Document Ingestion Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/v1/documents` | Multipart upload — validates, checksums (SHA-256), stores to S3 |
| `POST` | `/v1/documents/upload-url` | Returns a presigned PUT URL for direct client-to-S3 upload |
| `GET` | `/v1/documents/download-url` | Returns a presigned GET URL; validates `documents/` key prefix |
| `GET` | `/health` | Container liveness probe |

#### Database Schema (`apps/api/migrations/`)
Alembic async migration suite with asyncpg driver. Five production tables:

| Table | Purpose |
|---|---|
| `customers` | Canonical onboarding record with status enum |
| `documents` | Uploaded file metadata — storage key, SHA-256 checksum, uploader |
| `workflow_runs` | 10-state workflow FSM with JSONB error detail |
| `field_reviews` | HITL per-field review with `[0,1]` confidence constraint |
| `audit_logs` | Immutable event log — actor, action, entity, JSONB payload |

#### Object Storage (`packages/shared`)
- `StorageClient` — S3-compatible (AWS S3 and Cloudflare R2)
- Server-side `upload_bytes()` and presigned PUT/GET URL generation
- Storage key scoped as `documents/{customer_id}/{document_id}{ext}` — raw bucket paths never exposed
- Configurable entirely via `S3_*` environment variables

#### DevOps & Quality
- **Docker**: Non-root multi-stage images for `api` and `worker`; build context is repo root for uv workspace support; `PYTHONPATH` explicitly set
- **Docker Compose**: All secrets sourced from `.env`; no hardcoded credentials; health checks on all services
- **CI/CD** (GitHub Actions): Lint → type-check → test → build & push images; uses `uv sync --all-packages --dev`
- **Pre-commit**: ruff lint + format, mypy strict, standard file checks, no-commit-to-main guard
- **uv workspace**: `apps/api`, `apps/worker`, `packages/*` pinned in a single `uv.lock`

### In Progress / Planned

| Feature | Status |
|---|---|
| Celery task skeleton | Planned v1 |
| DB persistence for uploaded documents | Planned v1 |
| Workflow orchestration (LangGraph) | Planned v1 |
| Mapper / Validator / Auditor agents | Planned v1 |
| `POST /v1/workflows`, `GET /v1/workflows/{id}` | Planned v1 |
| `GET /v1/reviews`, `POST /v1/reviews/{id}` | Planned v1 |
| `POST /v1/sync/{workflow_id}` | Planned v1 |
| HITL dashboard (Next.js) | Planned v1 |
| Prometheus + Grafana observability | Planned v1 |
| Cost analytics, duplicate detection | Planned v1.1 |
| SSO, multi-tenant | Planned v1.2 |

---

## Repository Structure

```
onboard-ai/
├── apps/
│   ├── api/
│   │   ├── migrations/        # Alembic async migrations
│   │   └── src/api/
│   │       ├── db/            # SQLAlchemy ORM models + async session
│   │       ├── dependencies/  # JWT auth, DB session, S3 storage
│   │       └── routers/       # documents
│   ├── worker/                # Celery app + LangGraph agents (v1)
│   └── web/                   # Next.js HITL dashboard (v1)
├── packages/
│   ├── schemas/               # Canonical Pydantic read/write schemas
│   ├── prompts/               # LLM prompt templates
│   └── shared/                # StorageClient, structlog, prometheus-client
├── infra/                     # Terraform, CloudWatch
├── docs/                      # PRD, ADRs, architecture diagrams
├── tests/                     # Integration & e2e tests
└── docker-compose.yml
```

---

## Architecture

### 1. Multimodal Ingestion
- PDFs processed with Vision LLM
- CSV / Excel with deterministic parsing
- SQL dumps and JSON API payloads

### 2. Multi-Agent Orchestration (LangGraph)
- **Mapper agent** — field mapping, address normalization, entity grouping
- **Validator agent** — required fields, referential integrity, business rules
- **Auditor agent** — PII detection, masking recommendations, policy violations

### 3. Human-in-the-Loop
- Confidence thresholds route low-quality records to reviewer queue
- Field-level diff view with inline editing
- Full comment and approval trail

### 4. Production Synchronization
- Idempotent writes with change tracking
- Retry with exponential backoff
- Dead-letter queue for failed syncs

### 5. Observability
- Structured logs (structlog)
- Metrics (Prometheus / Grafana)
- LLM traces (LangSmith / Phoenix)
- Token cost tracking per workflow

---

## Local Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker / Podman + Compose

### Setup

```bash
git clone https://github.com/<your-handle>/onboard-ai.git
cd onboard-ai

# Install all workspace packages + dev tools
uv sync --all-packages --dev

# Install pre-commit hooks
uv run pre-commit install

# Configure environment — fill in POSTGRES_PASSWORD, JWT_SECRET, S3_*, OPENAI_API_KEY
cp .env.example .env

# Start Postgres and Redis
docker compose up postgres redis -d
```

### Database migrations

```bash
cd apps/api
uv run --package api alembic upgrade head
```

### Running services

```bash
# FastAPI (from repo root)
uv run --package api uvicorn api.main:app --reload

# Celery worker
uv run --package worker celery -A worker.main:celery_app worker --loglevel=info
```

### Full stack via Docker

```bash
docker compose up --build -d
docker compose logs -f api
docker compose logs -f worker
```

### Linting, formatting, type-checking

```bash
uv run ruff check .     # lint
uv run ruff format .    # format
uv run mypy .           # type-check (strict)
```

### Tests

```bash
uv run pytest
```

---

## Environment Variables

Copy `.env.example` to `.env`. Key variables:

| Variable | Description |
|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://` connection string |
| `REDIS_URL` | Redis for rate limiter and Celery broker |
| `JWT_SECRET` | HS256 signing secret |
| `S3_ENDPOINT_URL` | AWS S3, Cloudflare R2, or MinIO endpoint |
| `S3_ACCESS_KEY_ID` / `S3_SECRET_ACCESS_KEY` | Object storage credentials |
| `S3_BUCKET_NAME` | Bucket for uploaded documents |
| `OPENAI_API_KEY` | Used by extraction agents |

---

## Roadmap

| Version | Scope |
|---|---|
| **v1** | PDF/CSV ingestion, LangGraph orchestration, HITL dashboard, observability |
| **v1.1** | SQL dump support, duplicate detection, cost analytics |
| **v1.2** | SSO, multi-tenant support |
| **v2** | Real-time ingestion, custom policy engine, advanced entity resolution |

---

## License

MIT — see [LICENSE](LICENSE).
