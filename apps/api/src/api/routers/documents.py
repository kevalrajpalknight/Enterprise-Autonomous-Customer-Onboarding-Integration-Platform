from __future__ import annotations

import hashlib
import uuid
from enum import StrEnum
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel, Field

from api.config import settings
from api.dependencies.auth import CurrentUser, get_current_user

router = APIRouter(prefix="/documents", tags=["Documents"])

_ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/json",
    "application/octet-stream",  # generic fallback for SQL dumps
}


class DocumentType(StrEnum):
    pdf = "pdf"
    csv = "csv"
    excel = "excel"
    sql_dump = "sql_dump"
    json_api = "json_api"


class DocumentUploadResponse(BaseModel):
    document_id: str = Field(..., description="Stable UUID for this document")
    customer_id: str
    document_type: DocumentType
    filename: str
    size_bytes: int
    checksum_sha256: str
    message: str = "Document received and queued for processing"


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a customer document",
    description=(
        "Accepts a raw document file (PDF, CSV, Excel, SQL dump, or JSON) "
        "alongside metadata. The file is validated, checksummed, and queued "
        "for async extraction. Returns a document ID for status polling."
    ),
    dependencies=[
        Depends(
            RateLimiter(
                times=settings.rate_limit_requests,
                seconds=settings.rate_limit_window_seconds,
            )
        )
    ],
)
async def upload_document(
    customer_id: Annotated[str, Form(description="Target customer UUID")],
    document_type: Annotated[DocumentType, Form(description="Declared document type")],
    file: Annotated[UploadFile, File(description="Raw document file")],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> DocumentUploadResponse:
    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        accepted = sorted(_ALLOWED_CONTENT_TYPES)
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content type '{file.content_type}'. Accepted: {accepted}",
        )

    contents = await file.read()

    if len(contents) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {settings.max_upload_bytes // (1024 * 1024)} MB limit",
        )

    checksum = hashlib.sha256(contents).hexdigest()
    document_id = str(uuid.uuid4())

    # TODO: persist to storage (S3/R2) and enqueue Celery task
    # storage_key = f"raw/{customer_id}/{document_id}/{file.filename}"

    return DocumentUploadResponse(
        document_id=document_id,
        customer_id=customer_id,
        document_type=document_type,
        filename=file.filename or "unknown",
        size_bytes=len(contents),
        checksum_sha256=checksum,
    )
