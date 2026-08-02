from __future__ import annotations

import asyncio
import uuid
from typing import Any

from celery import Task
from shared.storage import StorageClient

from worker.config import settings
from worker.db import fetch_document_storage_key, save_parsed_payload
from worker.main import celery_app
from worker.vision.extract import extract_pdf_document
from worker.vision.factory import get_vision_client


def _get_storage_client() -> StorageClient:
    return StorageClient(
        endpoint_url=settings.s3_endpoint_url,
        access_key_id=settings.s3_access_key_id,
        secret_access_key=settings.s3_secret_access_key,
        bucket_name=settings.s3_bucket_name,
        region=settings.s3_region,
    )


async def _run_extraction(document_id: uuid.UUID) -> dict[str, Any]:
    storage_key = await fetch_document_storage_key(document_id)
    payload = extract_pdf_document(
        document_id=str(document_id),
        storage_key=storage_key,
        storage=_get_storage_client(),
        vision_client=get_vision_client(),
        dpi=settings.vision_page_dpi,
    )
    payload_dict = payload.model_dump()
    await save_parsed_payload(document_id, payload_dict)
    return payload_dict


@celery_app.task(name="worker.extract_document", bind=True, max_retries=3)
def extract_document(self: Task, document_id: str) -> dict[str, Any]:
    """Extract structured fields from a layout-heavy PDF using a vision LLM,
    then persist the result to documents.parsed_payload.
    """
    try:
        return asyncio.run(_run_extraction(uuid.UUID(document_id)))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=2**self.request.retries) from exc
