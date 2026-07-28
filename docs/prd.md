# PRD — OnboardAI
## Enterprise Autonomous Customer Onboarding & Integration Platform

**Author:** Keval Rajpal
**Role Target:** Forward Deployed Engineer (FDE) / Applied AI Engineer
**Version:** 0.1.0
**Status:** Draft for AI-assisted implementation

---

# 1. Executive Summary

OnboardAI is an enterprise-grade platform that automates customer onboarding by ingesting **unstructured and fragmented client data** (PDFs, CSV/Excel files, SQL dumps, and JSON APIs), transforming it into a **canonical schema**, validating it through **deterministic and AI-driven workflows**, routing low-confidence records to **human review**, and synchronizing approved records into production systems.

This project is intentionally designed to demonstrate the capabilities expected from a **Forward Deployed Engineer**:

- Client problem framing
- Systems architecture
- AI orchestration
- Backend engineering
- Frontend product thinking
- DevOps and reliability
- Observability and evaluation
- Security and governance

---

# 2. Problem Statement

Enterprise onboarding is often slow because:

- Customer data arrives in multiple inconsistent formats.
- Schemas evolve frequently.
- Validation rules are undocumented or scattered.
- Human operators manually reconcile conflicts.
- AI outputs are not auditable.
- There is limited visibility into quality, latency, and cost.

**Current state:** 2–10 days onboarding time with significant manual effort.

**Desired state:** 5–15 minutes for the majority of onboarding cases with full auditability.

---

# 3. Goals

## Primary Goals

- Ingest heterogeneous customer data.
- Extract structured information from unstructured documents.
- Normalize data into a canonical customer model.
- Validate business and compliance rules.
- Route uncertain records to human reviewers.
- Synchronize approved records to target systems.
- Provide end-to-end observability.

## Success Metrics

| Metric | Target |
|---|---|
| Auto-approved records | >70% |
| P95 processing latency | <30s |
| Extraction accuracy | >94% |
| Failed sync rate | <1% |
| Mean time to review | <3 min |
| Cost per onboarding | Track and optimize |

---

# 4. Non-Goals

- Full ERP implementation.
- Custom ML model training in v1.
- Real-time streaming ingestion.
- Multi-region deployment.
- Advanced identity verification.

---

# 5. User Personas

## Enterprise Operations Manager
Wants faster onboarding and visibility into bottlenecks.

## Compliance Officer
Needs audit trails, PII handling, and policy enforcement.

## Data Integration Engineer
Needs reliable APIs and schema management.

## Human Reviewer
Needs an efficient interface for resolving conflicts.

---

# 6. User Journey

1. Customer uploads documents or data.
2. System stores raw files.
3. Ingestion pipeline extracts structured payloads.
4. Mapper agent creates canonical records.
5. Validator agent checks business rules.
6. Auditor agent checks compliance and PII.
7. High-confidence records are auto-approved.
8. Low-confidence records go to HITL dashboard.
9. Reviewer corrects and approves.
10. Sync engine writes to production system.
11. Metrics, traces, and audit logs are recorded.

---

# 7. Functional Requirements

## 7.1 Authentication & Authorization
- JWT-based authentication
- Role-based access control
- Roles: Admin, Reviewer, Operator, ReadOnly

## 7.2 Document Ingestion
Supported inputs:
- PDF
- CSV
- Excel
- SQL dump
- JSON API

## 7.3 Storage
- Store original file
- Store parsed payload
- Store normalized payload
- Store audit history

## 7.4 AI Extraction
- Vision-capable extraction for PDFs
- Deterministic parsing for structured files
- Field-level confidence scores

## 7.5 Workflow Orchestration
- Stateful workflow
- Retry support
- Failure handling
- Manual intervention support

## 7.6 Human Review
- View source document
- Compare extracted vs corrected values
- Edit fields
- Approve or reject
- Leave comments

## 7.7 Synchronization
- Idempotent writes
- Retry with backoff
- Dead-letter queue
- Change tracking

## 7.8 Observability
- Request traces
- Queue depth
- Latency
- Token usage
- Error rates
- Cost metrics

---

# 8. AI Agent Responsibilities

## Mapper Agent
**Input:** Extracted payload
**Output:** Canonical customer record

Responsibilities:
- Field mapping
- Address normalization
- Entity grouping
- Missing field detection

## Validator Agent
**Input:** Canonical record
**Output:** Validation report

Responsibilities:
- Required fields
- Referential integrity
- Business rules
- Duplicate detection

## Auditor Agent
**Input:** Canonical record
**Output:** Compliance report

Responsibilities:
- PII detection
- Masking recommendations
- Suspicious values
- Policy violations

---

# 9. System Architecture

## Backend
- FastAPI
- Celery
- Redis
- PostgreSQL

## AI
- OpenAI Vision / LLM
- LangGraph

## Frontend
- Next.js
- Tailwind CSS

## DevOps
- Docker
- GitHub Actions
- AWS EC2
- AWS RDS
- AWS S3
- CloudWatch

## Observability
- Prometheus
- Grafana
- LangSmith / Phoenix

---

# 10. Repository Structure

\`\`\`
onboard-ai/
├── apps/
│   ├── api/
│   ├── worker/
│   └── web/
├── packages/
│   ├── schemas/
│   ├── prompts/
│   └── shared/
├── infra/
├── docs/
├── tests/
└── docker-compose.yml
\`\`\`

---

# 11. Database Design

## customers
- id
- external_id
- legal_name
- email
- phone
- status
- created_at

## documents
- id
- customer_id
- type
- storage_key
- checksum
- uploaded_at

## workflow_runs
- id
- customer_id
- state
- started_at
- completed_at

## field_reviews
- id
- workflow_run_id
- field_name
- extracted_value
- corrected_value
- confidence
- reviewer_id

## audit_logs
- id
- actor
- action
- entity_type
- entity_id
- metadata
- created_at

---

# 12. API Requirements

## Upload Document
\`\`\`
POST /v1/documents
\`\`\`

## Start Workflow
\`\`\`
POST /v1/workflows
\`\`\`

## Get Workflow
\`\`\`
GET /v1/workflows/{id}
\`\`\`

## List Review Queue
\`\`\`
GET /v1/reviews
\`\`\`

## Submit Review
\`\`\`
POST /v1/reviews/{id}
\`\`\`

## Trigger Sync
\`\`\`
POST /v1/sync/{workflow_id}
\`\`\`

---

# 13. Frontend Requirements

## Dashboard
- Workflow summary
- Queue metrics
- Error trends

## Review Workbench
- Source preview
- Field diff
- Confidence heatmap
- Inline editing

## Audit Viewer
- Timeline
- Actor
- Before/after values

---

# 14. DevOps Requirements

## Docker
- Multi-stage builds
- Health checks
- Non-root containers

## CI/CD
- Lint
- Type-check
- Unit tests
- Build images
- Deploy to EC2

## Environments
- local
- staging
- production

---

# 15. Reliability Requirements

- Exponential backoff
- Idempotent sync
- Circuit breaker for external APIs
- Dead-letter queue
- Graceful shutdown
- Correlation IDs

---

# 16. Security & Compliance

- HTTPS only
- JWT validation
- RBAC
- Secrets from environment
- PII masking in logs
- Audit trail for all manual changes
- Optional encryption hooks

---

# 17. Observability & Evaluation

## Metrics
- workflow_duration_seconds
- extraction_confidence
- review_queue_size
- sync_failures_total
- token_cost_usd

## Tracing
- request_id
- workflow_id
- task_id
- agent_name

## AI Evaluation
- Precision
- Recall
- Hallucination rate
- Human correction rate

---

# 18. Testing Strategy

## Unit
- Parsers
- Validators
- Mappers

## Integration
- Upload → Extract → Validate → Review → Sync

## Load
- 1,000 concurrent uploads

## Chaos
- Worker crash
- Redis unavailable
- External API timeout

---

# 19. Acceptance Criteria

A workflow is considered complete when:

- File uploaded successfully
- Payload extracted
- Canonical record generated
- Validation passed or reviewed
- Audit log written
- Sync completed
- Metrics emitted
- Trace available

---

# 20. Roadmap

## V1
- PDF/CSV ingestion
- LangGraph orchestration
- HITL dashboard
- Observability

## V1.1
- SQL dump support
- Duplicate detection
- Cost analytics

## V1.2
- Temporal migration
- SSO
- Multi-tenant support

## V2
- Real-time ingestion
- Custom policy engine
- Advanced entity resolution

---

# 21. Definition of Done

- Feature implemented
- Tests added
- OpenAPI updated
- Metrics added
- Logs added
- Docs updated
- Security reviewed
- Docker verified

---

# 22. FDE Evaluation Lens

This project should communicate the following to recruiters:

| Capability | Evidence |
|---|---|
| Client thinking | Problem framing section |
| Architecture | Multi-service design |
| AI engineering | Multi-agent workflow |
| Product thinking | HITL dashboard |
| Reliability | Retries, DLQ, idempotency |
| DevOps | CI/CD + AWS |
| Observability | Metrics + tracing |
| Governance | Audit + PII controls |

---

# 23. Engineering Philosophy

- Clarity > Cleverness
- Reliability > Demo quality
- Auditability > Automation hype
- Business outcomes > Model novelty
- Human control > Blind autonomy

---

# 24. Instructions for the AI Coding Agent

When implementing this project:

1. Prefer deterministic logic over LLMs when possible.
2. Keep modules small and testable.
3. Add type hints everywhere.
4. Emit structured logs.
5. Add metrics for every async step.
6. Make all external writes idempotent.
7. Never expose secrets in logs.
8. Write migration-safe database changes.
9. Update documentation with every feature.
10. Optimize for maintainability, not cleverness.

---

# 25. Final Vision

OnboardAI is not intended to be a toy AI demo.

It is a **portfolio-grade enterprise platform** that demonstrates how a Forward Deployed Engineer can:

- understand ambiguous customer problems,
- design scalable systems,
- combine AI with deterministic controls,
- keep humans in the loop,
- operate software in production,
- and communicate engineering decisions clearly.

The repository should look and feel like a real internal platform owned by an engineer who can take a project from **discovery → architecture → implementation → deployment → operations**.
