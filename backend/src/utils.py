from fastapi import HTTPException
import re


def sanitize_text(text: str) -> str:
    """Basic sanitization: trim, collapse whitespace, and remove control chars."""
    blob = (text or "").strip()
    # Collapse multiple spaces/newlines/tabs to single space
    blob = re.sub(r"\s+", " ", blob)
    # Remove non-printable control characters (except common whitespace already collapsed)
    blob = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", blob)
    return blob


def validate_request_inputs(product_name: str, product_details: str, target_market: str):
    """Validate inbound prompt inputs to guard against abuse and low-quality tasks."""
    name = (product_name or "").strip()
    details = (product_details or "").strip()
    market = (target_market or "").strip()

    # Presence and minimum length
    if len(name) < 3:
        raise HTTPException(status_code=400, detail="Product name must be at least 3 characters.")
    if len(details) < 20:
        raise HTTPException(status_code=400, detail="Product details must be at least 20 characters.")
    if len(market) < 3:
        raise HTTPException(status_code=400, detail="Target market must be at least 3 characters.")

    # Maximum length limits to avoid prompt/abuse
    if len(name) > 256:
        raise HTTPException(status_code=400, detail="Product name is too long (max 256 characters).")
    if len(market) > 256:
        raise HTTPException(status_code=400, detail="Target market is too long (max 256 characters).")
    if len(details) > 6000:
        raise HTTPException(status_code=400, detail="Product details are too long (max 6000 characters).")

    # Disallowed content keywords (simple heuristic)
    banned = [" malware ", " ransomware ", " exploit ", " bomb ", " ddos ", " botnet ", " drug ", " weapon "]
    blob = f" {name} {details} {market} ".lower()
    if any(term in blob for term in banned):
        raise HTTPException(status_code=400, detail="Input appears to contain disallowed content.")

    # Basic PII and link suppression (keep research task contextual)
    patterns = {
        "email": r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}",
        "phone": r"(?:\+\d{1,3}[ \-]?)?(?:\(\d{2,4}\)[ \-]?)?\d{3,4}[ \-]?\d{3,4}",
        "url": r"https?://|www\\."
    }
    if re.search(patterns["email"], blob, flags=re.I):
        raise HTTPException(status_code=400, detail="Please remove emails from inputs.")
    if re.search(patterns["phone"], blob, flags=re.I):
        raise HTTPException(status_code=400, detail="Please remove phone numbers from inputs.")
    if re.search(patterns["url"], blob, flags=re.I):
        raise HTTPException(status_code=400, detail="Please remove direct URLs from inputs; describe context instead.")

    # Reject repeated characters or nonsense
    if re.search(r"(.)\1{9,}", blob):  # 10+ repeated same char
        raise HTTPException(status_code=400, detail="Input appears spammy or low quality. Please revise.")


