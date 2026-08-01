from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel, Field
from shared.storage import ALLOWED_MIME_TYPES, StorageClient

from api.config import settings
from api.dependencies.auth import CurrentUser, get_current_user
from api.dependencies.storage import get_storage_client

router = APIRouter(prefix="/documents", tags=["Documents"])

_RATE_LIMIT = [
    Depends(
        RateLimiter(
            times=settings.rate_limit_requests,
            seconds=settings.rate_limit_window_seconds,
        )
    )
]


class DocumentType(StrEnum):
    pdf = "pdf"
    csv = "csv"
    excel = "excel"
    sql_dump = "sql_dump"
    json_api = "json_api"


# ── Response models ───────────────────────────────────────────────────────────


class DocumentUploadResponse(BaseModel):
    document_id: str = Field(..., description="Stable UUID for this document")
    customer_id: str
    document_type: DocumentType
    filename: str
    size_bytes: int
    checksum_sha256: str
    storage_key: str = Field(..., description="Opaque object key; never expose as a direct URL")
    message: str = "Document received and queued for processing"


class PresignedUploadResponse(BaseModel):
    document_id: str
    storage_key: str
    upload_url: str = Field(..., description="Presigned PUT URL — valid for 15 minutes")
    expires_at: datetime


class PresignedDownloadResponse(BaseModel):
    download_url: str = Field(..., description="Presigned GET URL — valid for 1 hour")
    expires_at: datetime


# ── Helpers ───────────────────────────────────────────────────────────────────


def _assert_allowed_mime(content_type: str | None) -> str:
    ct = content_type or ""
    if ct not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content type '{ct}'. Accepted: {sorted(ALLOWED_MIME_TYPES)}",
        )
    return ct


def _assert_size(data: bytes) -> None:
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {settings.max_upload_bytes // (1024 * 1024)} MB limit",
        )


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a customer document (server-side)",
    description=(
        "Accepts a raw document file via multipart form. The server validates, "
        "checksums, and stores the file to S3-compatible object storage, then "
        "queues it for async extraction. Returns a document ID for status polling."
    ),
    dependencies=_RATE_LIMIT,
)
async def upload_document(
    customer_id: Annotated[str, Form(description="Target customer UUID")],
    document_type: Annotated[DocumentType, Form(description="Declared document type")],
    file: Annotated[UploadFile, File(description="Raw document file")],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    storage: Annotated[StorageClient, Depends(get_storage_client)],
) -> DocumentUploadResponse:
    mime_type = _assert_allowed_mime(file.content_type)
    contents = await file.read()
    _assert_size(contents)

    document_id = str(uuid.uuid4())
    checksum = hashlib.sha256(contents).hexdigest()
    key = StorageClient.make_key(customer_id, document_id, mime_type)

    storage.upload_bytes(contents, key, mime_type)

    # TODO: persist Document row to DB and enqueue Celery extraction task

    return DocumentUploadResponse(
        document_id=document_id,
        customer_id=customer_id,
        document_type=document_type,
        filename=file.filename or "unknown",
        size_bytes=len(contents),
        checksum_sha256=checksum,
        storage_key=key,
    )


@router.post(
    "/upload-url",
    response_model=PresignedUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Request a presigned PUT URL for direct client upload",
    description=(
        "Pre-allocates a document ID and returns a presigned S3 PUT URL. "
        "The client uploads the file directly to object storage, keeping large "
        "files off the API server. Call POST /documents/confirm after upload."
    ),
    dependencies=_RATE_LIMIT,
)
async def request_upload_url(
    customer_id: Annotated[str, Form(description="Target customer UUID")],
    content_type: Annotated[str, Form(description="MIME type of the file to be uploaded")],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    storage: Annotated[StorageClient, Depends(get_storage_client)],
) -> PresignedUploadResponse:
    _assert_allowed_mime(content_type)

    document_id = str(uuid.uuid4())
    key = StorageClient.make_key(customer_id, document_id, content_type)
    ttl = 15 * 60
    upload_url = storage.presigned_upload_url(key, content_type, expires_in=ttl)

    return PresignedUploadResponse(
        document_id=document_id,
        storage_key=key,
        upload_url=upload_url,
        expires_at=datetime.now(UTC) + timedelta(seconds=ttl),
    )


@router.get(
    "/download-url",
    response_model=PresignedDownloadResponse,
    summary="Get a presigned GET URL for a stored document",
    description=(
        "Returns a time-limited presigned GET URL for a document already stored "
        "in object storage. The storage_key is the opaque key returned at upload "
        "time. Only keys scoped under documents/ are accepted."
    ),
)
async def get_download_url(
    storage_key: Annotated[str, Query(description="Opaque storage key returned at upload time")],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    storage: Annotated[StorageClient, Depends(get_storage_client)],
) -> PresignedDownloadResponse:
    # Prevent callers from requesting presigned URLs for arbitrary S3 keys
    if not storage_key.startswith("documents/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="storage_key must be scoped under documents/",
        )

    ttl = 60 * 60
    download_url = storage.presigned_download_url(storage_key, expires_in=ttl)
    return PresignedDownloadResponse(
        download_url=download_url,
        expires_at=datetime.now(UTC) + timedelta(seconds=ttl),
    )
