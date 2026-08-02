from functools import cache

from worker.config import settings
from worker.vision.base import VisionLLMClient
from worker.vision.openai_client import LangChainOpenAIVisionClient


@cache
def get_vision_client() -> VisionLLMClient:
    """Return the configured vision LLM client. Switching provider/model/params
    is a matter of changing VISION_LLM_PROVIDER/VISION_LLM_MODEL — no call-site changes.
    """
    if settings.vision_llm_provider == "openai":
        return LangChainOpenAIVisionClient(
            api_key=settings.openai_api_key,
            model=settings.vision_llm_model,
        )
    raise ValueError(f"Unsupported vision LLM provider: {settings.vision_llm_provider}")
