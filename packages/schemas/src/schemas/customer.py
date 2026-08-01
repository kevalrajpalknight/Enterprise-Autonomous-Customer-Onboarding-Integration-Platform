from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field


class CustomerStatus(StrEnum):
    pending = "pending"
    active = "active"
    rejected = "rejected"
    suspended = "suspended"


class CustomerCreate(BaseModel):
    external_id: str | None = Field(None, max_length=255)
    legal_name: str = Field(..., min_length=1, max_length=500)
    email: EmailStr
    phone: str | None = Field(None, max_length=50)


class CustomerRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    external_id: str | None
    legal_name: str
    email: str
    phone: str | None
    status: CustomerStatus
    created_at: datetime
    updated_at: datetime
