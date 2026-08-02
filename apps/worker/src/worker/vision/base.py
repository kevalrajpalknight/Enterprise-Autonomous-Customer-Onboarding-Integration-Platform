from __future__ import annotations

from abc import ABC, abstractmethod

from schemas.extraction import ExtractedField


class VisionLLMClient(ABC):
    """Provider-agnostic interface for extracting structured fields from a page image.

    Swapping model/provider/params means writing a new implementation of this
    class and pointing the factory at it — call sites never change.
    """

    @property
    @abstractmethod
    def model_name(self) -> str: ...

    @abstractmethod
    def extract_page(
        self,
        image_bytes: bytes,
        *,
        page_number: int,
        page_count: int,
    ) -> list[ExtractedField]:
        """Extract structured fields from a single rendered PDF page image (PNG bytes)."""
        ...
