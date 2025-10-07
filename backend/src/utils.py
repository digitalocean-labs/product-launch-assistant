from fastapi import HTTPException


def sanitize_text(text: str) -> str:
    return text.strip()


def validate_request_inputs(product_name: str, product_details: str, target_market: str):
    banned = [" malware ", " ransomware ", " exploit ", " bomb "]
    blob = f" {product_name} {product_details} {target_market} ".lower()
    if any(term in blob for term in banned):
        raise HTTPException(status_code=400, detail="Input appears to contain disallowed content.")


