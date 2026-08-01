"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-02 00:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _now = sa.func.now()

    # ── Enum types ────────────────────────────────────────────────────────────
    customer_status = postgresql.ENUM(
        "pending",
        "active",
        "rejected",
        "suspended",
        name="customer_status",
        create_type=False,
    )
    customer_status.create(op.get_bind(), checkfirst=True)

    document_type = postgresql.ENUM(
        "pdf",
        "csv",
        "excel",
        "sql_dump",
        "json_api",
        name="document_type",
        create_type=False,
    )
    document_type.create(op.get_bind(), checkfirst=True)

    workflow_state = postgresql.ENUM(
        "pending",
        "extracting",
        "mapping",
        "validating",
        "auditing",
        "review_required",
        "approved",
        "rejected",
        "synced",
        "failed",
        name="workflow_state",
        create_type=False,
    )
    workflow_state.create(op.get_bind(), checkfirst=True)

    # ── customers ─────────────────────────────────────────────────────────────
    op.create_table(
        "customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("legal_name", sa.String(500), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pending", "active", "rejected", "suspended", name="customer_status"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=_now,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=_now,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_customers"),
        sa.UniqueConstraint("external_id", name="uq_customers_external_id"),
        sa.UniqueConstraint("email", name="uq_customers_email"),
    )
    op.create_index("ix_customers_external_id", "customers", ["external_id"])
    op.create_index("ix_customers_email", "customers", ["email"])

    # ── documents ─────────────────────────────────────────────────────────────
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "type",
            sa.Enum("pdf", "csv", "excel", "sql_dump", "json_api", name="document_type"),
            nullable=False,
        ),
        sa.Column("storage_key", sa.String(1024), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("uploaded_by", sa.String(255), nullable=False),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=_now,
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            name="fk_documents_customer_id_customers",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_documents"),
    )
    op.create_index("ix_documents_customer_id", "documents", ["customer_id"])

    # ── workflow_runs ─────────────────────────────────────────────────────────
    op.create_table(
        "workflow_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "state",
            sa.Enum(
                "pending",
                "extracting",
                "mapping",
                "validating",
                "auditing",
                "review_required",
                "approved",
                "rejected",
                "synced",
                "failed",
                name="workflow_state",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("error_detail", postgresql.JSONB(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=_now,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=_now,
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["customers.id"],
            name="fk_workflow_runs_customer_id_customers",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name="fk_workflow_runs_document_id_documents",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_workflow_runs"),
    )
    op.create_index("ix_workflow_runs_customer_id", "workflow_runs", ["customer_id"])
    op.create_index("ix_workflow_runs_document_id", "workflow_runs", ["document_id"])
    op.create_index("ix_workflow_runs_state", "workflow_runs", ["state"])

    # ── field_reviews ─────────────────────────────────────────────────────────
    op.create_table(
        "field_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workflow_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("field_name", sa.String(255), nullable=False),
        sa.Column("extracted_value", sa.Text(), nullable=True),
        sa.Column("corrected_value", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("reviewer_id", sa.String(255), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=_now,
        ),
        sa.CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="ck_field_reviews_confidence_range",
        ),
        sa.ForeignKeyConstraint(
            ["workflow_run_id"],
            ["workflow_runs.id"],
            name="fk_field_reviews_workflow_run_id_workflow_runs",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_field_reviews"),
    )
    op.create_index("ix_field_reviews_workflow_run_id", "field_reviews", ["workflow_run_id"])

    # ── audit_logs ────────────────────────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor", sa.String(255), nullable=False),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=_now,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_audit_logs"),
    )
    op.create_index("ix_audit_logs_entity", "audit_logs", ["entity_type", "entity_id"])
    op.create_index("ix_audit_logs_actor_created", "audit_logs", ["actor", "created_at"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("field_reviews")
    op.drop_table("workflow_runs")
    op.drop_table("documents")
    op.drop_table("customers")

    op.execute("DROP TYPE IF EXISTS workflow_state")
    op.execute("DROP TYPE IF EXISTS document_type")
    op.execute("DROP TYPE IF EXISTS customer_status")
