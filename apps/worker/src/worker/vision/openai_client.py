from __future__ import annotations

import base64

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from prompts import VISION_EXTRACTION_SYSTEM_PROMPT, VISION_EXTRACTION_USER_PROMPT_TEMPLATE
from pydantic import BaseModel, Field, SecretStr
from schemas.extraction import ExtractedField

from worker.vision.base import VisionLLMClient


class _PageField(BaseModel):
    name: str
    value: str | None
    confidence: float = Field(ge=0.0, le=1.0)


class _PageExtraction(BaseModel):
    fields: list[_PageField]


class LangChainOpenAIVisionClient(VisionLLMClient):
    """Vision extraction backed by an OpenAI-compatible chat model via langchain-openai."""

    def __init__(self, api_key: str, model: str, temperature: float = 0.0) -> None:
        self._model = model
        self._llm = ChatOpenAI(api_key=SecretStr(api_key), model=model, temperature=temperature)
        self._structured_llm = self._llm.with_structured_output(_PageExtraction)

    @property
    def model_name(self) -> str:
        return self._model

    def extract_page(
        self,
        image_bytes: bytes,
        *,
        page_number: int,
        page_count: int,
    ) -> list[ExtractedField]:
        image_b64 = base64.b64encode(image_bytes).decode("ascii")
        user_prompt = VISION_EXTRACTION_USER_PROMPT_TEMPLATE.format(
            page_number=page_number, page_count=page_count
        )
        messages = [
            SystemMessage(content=VISION_EXTRACTION_SYSTEM_PROMPT),
            HumanMessage(
                content=[
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                    },
                ]
            ),
        ]
        result = self._structured_llm.invoke(messages)
        assert isinstance(result, _PageExtraction)
        return [
            ExtractedField(
                name=field.name,
                value=field.value,
                confidence=field.confidence,
                source_page=page_number,
            )
            for field in result.fields
        ]
