from __future__ import annotations

from collections.abc import Generator

import pytest
from worker.config import settings
from worker.vision.factory import get_vision_client
from worker.vision.openai_client import LangChainOpenAIVisionClient


@pytest.fixture(autouse=True)
def _clear_cache() -> Generator[None]:
    get_vision_client.cache_clear()
    yield
    get_vision_client.cache_clear()


def test_openai_provider_returns_langchain_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "vision_llm_provider", "openai")
    monkeypatch.setattr(settings, "vision_llm_model", "gpt-4o")
    monkeypatch.setattr(settings, "openai_api_key", "sk-test")

    client = get_vision_client()

    assert isinstance(client, LangChainOpenAIVisionClient)
    assert client.model_name == "gpt-4o"


def test_unsupported_provider_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "vision_llm_provider", "anthropic")

    with pytest.raises(ValueError, match="Unsupported vision LLM provider"):
        get_vision_client()
