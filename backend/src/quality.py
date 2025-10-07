from .config import MARKET_RESEARCH_MIN_CHARS


def assess_quality(text: str, minimum_characters: int = MARKET_RESEARCH_MIN_CHARS) -> str:
    blob = (text or "").strip()
    if len(blob) < minimum_characters:
        return "poor"
    failure_indicators = [
        "⚠️ generation failed",
        "generation failed after retries",
        "api error:",
        "search api error:",
        "web search unavailable:",
        "failed to generate",
        "unable to generate",
        "generation error:",
        "api unavailable"
    ]
    blob_lower = blob.lower()
    for indicator in failure_indicators:
        if indicator in blob_lower:
            return "poor"
    section_indicators = ["1.", "2.", "3.", "•", "-", "*", "##", "###"]
    has_structure = any(indicator in blob for indicator in section_indicators)
    placeholder_phrases = [
        "placeholder text",
        "sample content",
        "example text",
        "lorem ipsum",
        "to be filled",
        "coming soon"
    ]
    has_placeholders = any(phrase in blob_lower for phrase in placeholder_phrases)
    word_count = len(blob.split())
    min_words = minimum_characters // 6
    if has_placeholders:
        return "poor"
    if word_count < min_words:
        return "poor"
    if has_structure or word_count >= min_words * 1.5:
        return "good"
    return "good"


