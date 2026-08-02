from __future__ import annotations

from typing import Protocol

from schemas.extraction import ExtractedField, ExtractedPayload

from worker.vision.base import VisionLLMClient
from worker.vision.renderer import render_pdf_pages_to_png


class DocumentStorage(Protocol):
    def download_bytes(self, key: str) -> bytes: ...


def extract_pdf_document(
    *,
    document_id: str,
    storage_key: str,
    storage: DocumentStorage,
    vision_client: VisionLLMClient,
    dpi: int = 200,
) -> ExtractedPayload:
    """Download a PDF from object storage, render each page to an image, and run
    vision extraction on every page. Fields from all pages are merged into one payload.
    """
    pdf_bytes = storage.download_bytes(storage_key)
    page_images = render_pdf_pages_to_png(pdf_bytes, dpi=dpi)

    fields: list[ExtractedField] = []
    for page_number, image_bytes in enumerate(page_images, start=1):
        fields.extend(
            vision_client.extract_page(
                image_bytes,
                page_number=page_number,
                page_count=len(page_images),
            )
        )

    return ExtractedPayload(
        document_id=document_id,
        fields=fields,
        model=vision_client.model_name,
        page_count=len(page_images),
    )
