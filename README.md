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

## Repository Structure

```
onboard-ai/
├── apps/
│   ├── api/          # FastAPI application
│   ├── worker/       # Celery async workers + LangGraph agents
│   └── web/          # Next.js HITL dashboard (v1)
├── packages/
│   ├── schemas/      # Canonical Pydantic schemas (shared)
│   ├── prompts/      # LLM prompt templates
│   └── shared/       # Logging, observability, utilities
├── infra/            # Docker, Terraform, CI/CD
├── docs/             # PRD, ADRs, architecture diagrams
├── tests/            # Integration & e2e tests
└── docker-compose.yml
```

---

## Architecture

### 1. Multimodal Ingestion
- PDFs (Vision LLM)
- CSV / Excel
- SQL dumps
- JSON APIs

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

## Business Outcomes

- Reduce onboarding turnaround from **days to minutes**
- Handle **schema evolution without code rewrites**
- Detect **PII and compliance risks automatically**
- Route low-confidence cases to human operators
- Produce **auditable synchronization logs**
- Measure extraction quality, latency, and token cost

---

## Local Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Docker + Docker Compose

### Setup

```bash
# Clone the repo
git clone https://github.com/<your-handle>/onboard-ai.git
cd onboard-ai

# Install all workspace dependencies (including dev tools)
uv sync --all-packages

# Install pre-commit hooks
uv run pre-commit install

# Start infrastructure (Postgres + Redis)
docker compose up -d
```

### Running services

```bash
# API server
uv run --package api uvicorn api.main:app --reload

# Celery worker
uv run --package worker celery -A worker.main worker --loglevel=info
```

### Linting & formatting

```bash
uv run ruff check .          # lint
uv run ruff format .         # format
uv run mypy .                # type-check
```

### Tests

```bash
uv run pytest
```

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
