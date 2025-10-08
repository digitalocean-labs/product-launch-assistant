import time
import asyncio
from .config import llm, llm_fallback


def generate_with_retries(prompt: str, section_key: str, state: dict, max_retries: int = 2) -> dict:
    retries = state.setdefault("retries", {})
    model_used = state.setdefault("model_used", {})
    attempts = 0
    backoff_seconds = 0.5

    while attempts <= max_retries:
        try:
            content = llm.invoke(prompt).content
            state[section_key] = content
            model_used[section_key] = getattr(llm, "model", "primary")
            retries[section_key] = attempts
            return state
        except Exception:
            attempts += 1
            retries[section_key] = attempts
            time.sleep(backoff_seconds)
            backoff_seconds = min(backoff_seconds * 2, 2.0)

    try:
        content = llm_fallback.invoke(prompt).content
        state[section_key] = content
        model_used[section_key] = getattr(llm_fallback, "model", "fallback")
        return state
    except Exception:
        state[section_key] = "⚠️ Generation failed after retries and fallback."
        model_used[section_key] = "failed"
        return state


async def generate_with_retries_async(prompt: str, section_key: str, state: dict, max_retries: int = 2) -> dict:
    retries = state.setdefault("retries", {})
    model_used = state.setdefault("model_used", {})
    attempts = 0
    backoff_seconds = 0.5

    while attempts <= max_retries:
        try:
            content = await llm.ainvoke(prompt)
            state[section_key] = content.content
            model_used[section_key] = getattr(llm, "model", "primary")
            retries[section_key] = attempts
            return state
        except Exception:
            attempts += 1
            retries[section_key] = attempts
            await asyncio.sleep(backoff_seconds)
            backoff_seconds = min(backoff_seconds * 2, 2.0)

    try:
        content = await llm_fallback.ainvoke(prompt)
        state[section_key] = content.content
        model_used[section_key] = getattr(llm_fallback, "model", "fallback")
        return state
    except Exception:
        state[section_key] = "⚠️ Generation failed after retries and fallback."
        model_used[section_key] = "failed"
        return state


