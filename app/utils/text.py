import json
import re
from typing import Any, Dict, Set


def safe_filename(value: str, max_length: int = 80) -> str:
    """Convert a string into a safe lowercase filename."""
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_").lower()
    return (cleaned or "document")[:max_length]


def strip_code_fences(text: str) -> str:
    """Remove ```json ... ``` wrappers if Gemini returns them."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def parse_json_safely(text: str, default: Dict[str, Any]) -> Dict[str, Any]:

    try:
        return json.loads(strip_code_fences(text))
    except Exception:
        return default


def word_set(text: str) -> Set[str]:
    """Return meaningful lowercase words for simple overlap calculations."""
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9]{2,}", text.lower())
    stop_words = {
        "the", "and", "for", "with", "this", "that", "from", "are", "was",
        "were", "you", "your", "have", "has", "but", "not", "can", "will",
    }
    return {word for word in words if word not in stop_words}
