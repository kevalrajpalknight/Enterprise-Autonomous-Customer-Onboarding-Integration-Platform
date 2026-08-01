from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class DocumentType(StrEnum):
    pdf = "pdf"
    csv = "csv"
    excel = "excel"
    sql_dump = "sql_dump"
    json_api = "json_api"


class DocumentRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    customer_id: uuid.UUID
    type: DocumentType
    storage_key: str
    checksum: str
    uploaded_by: str
    uploaded_at: datetime
