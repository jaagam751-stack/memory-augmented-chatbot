"""
Why this file exists:
    Dynamic tool calling means the agent should decide whether a tool is needed
    instead of always calling every tool.

Responsibility:
    - Ask Gemini to choose tavily_search, weather, or none.
    - Provide keyword fallback routing for reliability.
    - Execute the selected tool.

How it connects to the project:
    The LangGraph Tool Calling node uses ToolRouter to decide and run tools.
"""

import re
from typing import Dict

from app.prompts.prompts import TOOL_ROUTER_PROMPT
from app.tools.tavily_tool import tavily_search
from app.tools.weather_tool import get_weather
from app.utils.gemini import get_llm
from app.utils.text import parse_json_safely


class ToolRouter:
    """Routes questions to tools only when needed."""

    def decide(self, question: str) -> Dict[str, str]:
        """Return a tool decision dictionary."""
        fallback = self._keyword_decision(question)
        try:
            llm = get_llm(temperature=0)
            response = llm.invoke(TOOL_ROUTER_PROMPT.format(question=question))
            decision = parse_json_safely(response.content, default=fallback)
            if decision.get("tool") not in {"tavily_search", "weather", "none"}:
                return fallback
            return decision
        except Exception:
            return fallback

    def _keyword_decision(self, question: str) -> Dict[str, str]:
        q = question.lower()
        if "weather" in q or "temperature" in q:
            city = self._extract_city(question)
            return {"tool": "weather", "query": city, "reason": "Question asks for weather."}
        if any(word in q for word in ["latest", "current", "today", "news", "search web", "recent"]):
            return {"tool": "tavily_search", "query": question, "reason": "Question may need current web data."}
        return {"tool": "none", "query": "", "reason": "Local context should be enough."}

    def _extract_city(self, question: str) -> str:
        """Simple city extraction for beginner project."""
        match = re.search(r"(?:weather|temperature)\s+(?:in|at|for)?\s*([A-Za-z\s]+)", question, re.IGNORECASE)
        if match:
            city = match.group(1).strip().rstrip("?")
            return city or "Jaipur"
        return "Jaipur"

    def run(self, decision: Dict[str, str]) -> Dict[str, object]:
        """Execute the selected tool."""
        tool = decision.get("tool", "none")
        query = decision.get("query", "")
        if tool == "weather":
            return get_weather(query or "Jaipur")
        if tool == "tavily_search":
            return tavily_search(query)
        return {"success": True, "output": "No external tool was needed."}
