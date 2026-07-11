"""
Why this file exists:
    Neo4j needs structured nodes and relationships, but scraped documents are raw
    text. This file converts text into a small graph structure.

Responsibility:
    - Ask Gemini to extract entities and relationships as JSON.
    - Provide a simple fallback entity extractor if LLM parsing fails.

How it connects to the project:
    The ingestion service calls this extractor and then sends the result to
    Neo4jGraphClient for storage.
"""

import re
from typing import Dict, List

from app.prompts.prompts import KG_EXTRACTION_PROMPT
from app.utils.gemini import get_llm
from app.utils.text import parse_json_safely


def _fallback_entities(text: str) -> List[Dict[str, str]]:
    """Very simple fallback: collect repeated capitalized phrases."""
    names = re.findall(r"\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2}\b", text)
    unique = []
    for name in names:
        if name not in unique and len(name) > 2:
            unique.append(name)
    return [{"name": name, "type": "Other"} for name in unique[:20]]


def extract_knowledge_graph(text: str) -> Dict[str, List[Dict[str, str]]]:
    """Extract entities and relationships from text using Gemini."""
    # Limit text so the extraction prompt stays fast and free-tier friendly.
    short_text = text[:6000]
    default = {"entities": _fallback_entities(short_text), "relationships": []}

    try:
        llm = get_llm(temperature=0)
        response = llm.invoke(KG_EXTRACTION_PROMPT.format(text=short_text))
        parsed = parse_json_safely(response.content, default=default)
        parsed.setdefault("entities", [])
        parsed.setdefault("relationships", [])
        return parsed
    except Exception:
        return default
