from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base import Base


class FieldReview(Base):
    __tablename__ = "field_reviews"
    __table_args__ = (
        CheckConstraint("confidence >= 0.0 AND confidence <= 1.0", name="confidence_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    extracted_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    corrected_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reviewer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)  # JWT sub
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    workflow_run: Mapped[WorkflowRun] = relationship(
        "WorkflowRun", back_populates="field_reviews", lazy="noload"
    )


from api.db.models.workflow_run import WorkflowRun  # noqa: E402
