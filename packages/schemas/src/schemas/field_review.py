from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FieldReviewRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    workflow_run_id: uuid.UUID
    field_name: str
    extracted_value: str | None
    corrected_value: str | None
    confidence: float
    reviewer_id: str | None
    reviewed_at: datetime | None
    comment: str | None
    created_at: datetime


class FieldReviewSubmit(BaseModel):
    corrected_value: str | None = None
    comment: str | None = None
    approved: bool = Field(..., description="True to approve, False to reject the field value")
