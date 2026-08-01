from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel


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


class WorkflowRunCreate(BaseModel):
    customer_id: uuid.UUID
    document_id: uuid.UUID | None = None


class WorkflowRunRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    customer_id: uuid.UUID
    document_id: uuid.UUID | None
    state: WorkflowState
    error_detail: dict[str, Any] | None
    started_at: datetime
    completed_at: datetime | None
    updated_at: datetime
