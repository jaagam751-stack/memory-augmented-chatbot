"""
Why this file exists:
    The chatbot sometimes needs fresh web information not present in local
    documents. Tavily provides a free-tier search API.

Responsibility:
    - Call Tavily Search API.
    - Return a short readable summary of search results.

How it connects to the project:
    The LangGraph Tool Calling node uses this tool when the router chooses
    tavily_search.
"""

from typing import Dict, List

import requests

from app.utils.config import settings


def tavily_search(query: str, max_results: int = 3) -> Dict[str, object]:
    """Search the web using Tavily's free API tier."""
    if not settings.tavily_api_key:
        return {"success": False, "output": "TAVILY_API_KEY is missing."}

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": settings.tavily_api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": max_results,
            },
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        results: List[Dict] = data.get("results", [])
        lines = [f"Search query: {query}"]
        for item in results:
            lines.append(f"- {item.get('title')} ({item.get('url')}): {item.get('content')}")
        return {"success": True, "output": "\n".join(lines), "raw": results}
    except Exception as exc:
        return {"success": False, "output": f"Tavily search failed: {exc}"}
