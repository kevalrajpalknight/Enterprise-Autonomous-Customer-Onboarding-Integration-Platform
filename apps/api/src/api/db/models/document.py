from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base import Base


class DocumentType(StrEnum):
    pdf = "pdf"
    csv = "csv"
    excel = "excel"
    sql_dump = "sql_dump"
    json_api = "json_api"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, name="document_type"), nullable=False
    )
    storage_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 hex
    uploaded_by: Mapped[str] = mapped_column(String(255), nullable=False)  # JWT sub
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    customer: Mapped[Customer] = relationship("Customer", back_populates="documents", lazy="noload")
    workflow_runs: Mapped[list[WorkflowRun]] = relationship(
        "WorkflowRun", back_populates="document", lazy="noload"
    )


from api.db.models.customer import Customer  # noqa: E402
from api.db.models.workflow_run import WorkflowRun  # noqa: E402
