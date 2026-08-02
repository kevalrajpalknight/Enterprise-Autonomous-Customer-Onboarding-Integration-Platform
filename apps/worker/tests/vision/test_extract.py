from __future__ import annotations

from typing import cast

import fitz
from schemas.extraction import ExtractedField
from worker.vision.base import VisionLLMClient
from worker.vision.extract import extract_pdf_document


def _make_pdf(num_pages: int) -> bytes:
    doc = fitz.open()
    for i in range(num_pages):
        page = doc.new_page()
        page.insert_text((72, 72), f"Page {i + 1}")
    pdf_bytes = cast(bytes, doc.tobytes())
    doc.close()
    return pdf_bytes


class _FakeStorage:
    def __init__(self, pdf_bytes: bytes) -> None:
        self._pdf_bytes = pdf_bytes

    def download_bytes(self, key: str) -> bytes:
        return self._pdf_bytes


class _FakeVisionClient(VisionLLMClient):
    @property
    def model_name(self) -> str:
        return "fake-vision-model"

    def extract_page(
        self, image_bytes: bytes, *, page_number: int, page_count: int
    ) -> list[ExtractedField]:
        return [
            ExtractedField(
                name="legal_name",
                value=f"Acme Corp (page {page_number})",
                confidence=0.9,
                source_page=page_number,
            )
        ]


def test_merges_fields_across_all_pages() -> None:
    payload = extract_pdf_document(
        document_id="11111111-1111-1111-1111-111111111111",
        storage_key="documents/customer/doc.pdf",
        storage=_FakeStorage(_make_pdf(2)),
        vision_client=_FakeVisionClient(),
    )

    assert payload.page_count == 2
    assert payload.model == "fake-vision-model"
    assert [f.source_page for f in payload.fields] == [1, 2]
    assert payload.fields[0].value == "Acme Corp (page 1)"
