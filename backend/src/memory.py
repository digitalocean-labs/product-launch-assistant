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



