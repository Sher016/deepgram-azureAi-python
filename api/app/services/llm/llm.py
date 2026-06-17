from functools import lru_cache

from langchain_openai import ChatOpenAI

from app.core.config import get_settings


@lru_cache
def get_llm() -> ChatOpenAI:
    """
    Returns a cached LangChain LLM instance.
    Swap provider here only — nothing else changes.
    """
    settings = get_settings()
    return ChatOpenAI(
        base_url=settings.azure_openai_base_url,
        api_key=settings.azure_openai_api_key,
        # api_version=settings.azure_openai_api_version,
        model=settings.azure_openai_model,
        temperature=0,
        max_tokens=1000,
        timeout=60,
        max_retries=3,
    )
