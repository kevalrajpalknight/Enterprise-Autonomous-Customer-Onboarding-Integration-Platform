from __future__ import annotations

from pydantic import BaseModel, Field


class ExtractedField(BaseModel):
    name: str
    value: str | None
    confidence: float = Field(ge=0.0, le=1.0)
    source_page: int = Field(ge=1, description="1-indexed PDF page the value was read from")


class ExtractedPayload(BaseModel):
    document_id: str
    fields: list[ExtractedField]
    model: str = Field(description="Vision LLM model identifier used for extraction")
    page_count: int = Field(ge=0)
