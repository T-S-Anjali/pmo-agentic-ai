"""
LLM Factory — returns the correct LangChain chat model based on LLM_PROVIDER.

All agents call get_llm() instead of instantiating a model directly.
Switch providers by changing LLM_PROVIDER in .env — no code changes needed.
"""
from functools import lru_cache
from langchain_core.language_models import BaseChatModel
from app.core.config import settings


@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.2) -> BaseChatModel:
    provider = settings.LLM_PROVIDER.lower()

    if provider == "ollama":
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            from langchain_community.chat_models import ChatOllama
        
        return ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=temperature,
        )

    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-4o",
            api_key=settings.OPENAI_API_KEY,
            temperature=temperature,
        )

    elif provider == "azure_openai":
        from langchain_openai import AzureChatOpenAI
        return AzureChatOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            api_key=settings.AZURE_OPENAI_API_KEY,
            temperature=temperature,
        )

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER='{provider}'. "
            "Valid options: ollama | openai | azure_openai"
        )
