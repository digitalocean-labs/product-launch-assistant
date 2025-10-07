from datetime import datetime
from .config import llm


MAX_RECENT_EVENTS = 12
SUMMARY_MIN_CHARS = 1200


def log_step(state: dict, section_key: str, content: str):
    event = {
        "timestamp": datetime.now().isoformat(),
        "section": section_key,
        "preview": (content or "")[:240]
    }
    recent = state.setdefault("recent_events", [])
    recent.append(event)
    if len(recent) > MAX_RECENT_EVENTS:
        state["recent_events"] = recent[-MAX_RECENT_EVENTS:]


def maybe_update_memory_summary(state: dict) -> dict:
    existing = state.get("memory_summary", "")
    corpus_parts = [
        state.get("market_research", "")[:2000],
        state.get("pricing_strategy", "")[:1200],
        state.get("launch_plan", "")[:1200],
        "\nRecent events:\n" + "\n".join([e.get("preview", "") for e in state.get("recent_events", [])[-6:]])
    ]
    corpus = "\n\n".join([p for p in corpus_parts if p])
    if len(existing) < SUMMARY_MIN_CHARS and len(corpus) < SUMMARY_MIN_CHARS:
        return state
    prompt = (
        "Summarize the product context and decisions so far in 10-14 bullet points. "
        "Preserve key facts, constraints, and decisions. Keep under 400-600 words.\n\n"
        f"Existing summary (if any): {existing}\n\n"
        f"New context to compress:\n{corpus}"
    )
    try:
        summary = llm.invoke(prompt).content
        state["memory_summary"] = summary
    except Exception:
        pass
    return state


