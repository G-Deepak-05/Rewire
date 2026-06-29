"""
LLM client — wraps LiteLLM for OpenRouter/any provider.
API key is loaded from environment variable, never hardcoded.
"""

import time
import litellm
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Configure LiteLLM
litellm.drop_params = True


async def get_llm_response(prompt: str, **kwargs) -> str:
    """Get a single LLM response for a prompt string."""
    start_time = time.time()
    try:
        response = await litellm.acompletion(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", settings.llm_temperature),
            max_tokens=kwargs.get("max_tokens", settings.llm_max_tokens),
            api_key=settings.llm_api_key,
            api_base=settings.llm_api_base,
        )
        elapsed = time.time() - start_time
        logger.info(f"AI Processing Time (Single): {elapsed:.2f}s", model=settings.llm_model)
        return response.choices[0].message.content
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"LLM completion failed after {elapsed:.2f}s", error=str(e), model=settings.llm_model)
        raise


async def get_llm_chat_response(messages: list[dict], **kwargs) -> str:
    """Get LLM response for a multi-turn conversation."""
    start_time = time.time()
    try:
        response = await litellm.acompletion(
            model=settings.llm_model,
            messages=messages,
            temperature=kwargs.get("temperature", settings.llm_temperature),
            max_tokens=kwargs.get("max_tokens", settings.llm_max_tokens),
            api_key=settings.llm_api_key,
            api_base=settings.llm_api_base,
        )
        elapsed = time.time() - start_time
        logger.info(f"AI Processing Time (Chat): {elapsed:.2f}s", model=settings.llm_model)
        return response.choices[0].message.content
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"LLM chat completion failed after {elapsed:.2f}s", error=str(e), model=settings.llm_model)
        raise


async def get_llm_streaming_response(messages: list[dict], **kwargs):
    """Get streaming LLM response — yields chunks."""
    try:
        response = await litellm.acompletion(
            model=settings.llm_model,
            messages=messages,
            temperature=kwargs.get("temperature", settings.llm_temperature),
            max_tokens=kwargs.get("max_tokens", settings.llm_max_tokens),
            api_key=settings.llm_api_key,
            api_base=settings.llm_api_base,
            stream=True,
        )
        async for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        logger.error("LLM streaming failed", error=str(e), model=settings.llm_model)
        raise
