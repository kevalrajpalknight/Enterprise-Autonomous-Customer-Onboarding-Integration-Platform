from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuditLogRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    actor: str
    action: str
    entity_type: str
    entity_id: uuid.UUID
    event_metadata: dict[str, Any] = Field(alias="metadata")
    created_at: datetime


class AuditLogCreate(BaseModel):
    actor: str = Field(..., max_length=255)
    action: str = Field(..., max_length=255)
    entity_type: str = Field(..., max_length=100)
    entity_id: uuid.UUID
    event_metadata: dict[str, Any] = Field(default_factory=dict)
