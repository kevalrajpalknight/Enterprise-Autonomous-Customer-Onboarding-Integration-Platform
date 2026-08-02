from __future__ import annotations

from typing import cast

import fitz
from worker.vision.renderer import render_pdf_pages_to_png


def _make_pdf(num_pages: int) -> bytes:
    doc = fitz.open()
    for i in range(num_pages):
        page = doc.new_page()
        page.insert_text((72, 72), f"Page {i + 1}")
    pdf_bytes = cast(bytes, doc.tobytes())
    doc.close()
    return pdf_bytes


def test_renders_one_png_per_page() -> None:
    images = render_pdf_pages_to_png(_make_pdf(3), dpi=100)

    assert len(images) == 3
    for image in images:
        assert image.startswith(b"\x89PNG\r\n\x1a\n")


def test_renders_single_page() -> None:
    images = render_pdf_pages_to_png(_make_pdf(1), dpi=150)

    assert len(images) == 1
