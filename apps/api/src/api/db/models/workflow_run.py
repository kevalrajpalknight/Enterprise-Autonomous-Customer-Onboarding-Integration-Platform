from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base import Base


class WorkflowState(StrEnum):
    pending = "pending"
    extracting = "extracting"
    mapping = "mapping"
    validating = "validating"
    auditing = "auditing"
    review_required = "review_required"
    approved = "approved"
    rejected = "rejected"
    synced = "synced"
    failed = "failed"


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    state: Mapped[WorkflowState] = mapped_column(
        Enum(WorkflowState, name="workflow_state"),
        nullable=False,
        default=WorkflowState.pending,
        server_default=WorkflowState.pending.value,
        index=True,
    )
    # Stores structured failure details; null on success
    error_detail: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    customer: Mapped[Customer] = relationship(
        "Customer", back_populates="workflow_runs", lazy="noload"
    )
    document: Mapped[Document | None] = relationship(
        "Document", back_populates="workflow_runs", lazy="noload"
    )
    field_reviews: Mapped[list[FieldReview]] = relationship(
        "FieldReview", back_populates="workflow_run", lazy="noload"
    )


from api.db.models.customer import Customer  # noqa: E402
from api.db.models.document import Document  # noqa: E402
from api.db.models.field_review import FieldReview  # noqa: E402
