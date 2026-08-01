from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base import Base


class CustomerStatus(StrEnum):
    pending = "pending"
    active = "active"
    rejected = "rejected"
    suspended = "suspended"


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )
    legal_name: Mapped[str] = mapped_column(String(500), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[CustomerStatus] = mapped_column(
        Enum(CustomerStatus, name="customer_status"),
        nullable=False,
        default=CustomerStatus.pending,
        server_default=CustomerStatus.pending.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    documents: Mapped[list[Document]] = relationship(
        "Document", back_populates="customer", lazy="noload"
    )
    workflow_runs: Mapped[list[WorkflowRun]] = relationship(
        "WorkflowRun", back_populates="customer", lazy="noload"
    )


from api.db.models.document import Document  # noqa: E402
from api.db.models.workflow_run import WorkflowRun  # noqa: E402
