from __future__ import annotations

import fitz  # PyMuPDF


def render_pdf_pages_to_png(pdf_bytes: bytes, dpi: int = 200) -> list[bytes]:
    """Render each page of a PDF to a PNG image at the given DPI, in page order."""
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    images: list[bytes] = []
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            pixmap = page.get_pixmap(matrix=matrix)
            images.append(pixmap.tobytes("png"))
    return images
