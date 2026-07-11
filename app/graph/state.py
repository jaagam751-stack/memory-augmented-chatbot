"""
Why this file exists:
    LangGraph passes a shared state object from node to node. Defining it clearly
    helps beginners understand what data moves through the workflow.

Responsibility:
    - Define the AgentState TypedDict.
    - Document fields used by memory, RAG, tools, LLM, and evaluation nodes.

How it connects to the project:
    app/graph/workflow.py imports AgentState when building the LangGraph workflow.
"""

from typing import Dict, List, TypedDict


class AgentState(TypedDict, total=False):
    """State shared between LangGraph nodes."""

    user_id: str
    question: str
    memory: str
    context: str
    graph_context: str
    retrieved_docs: List[Dict[str, str]]
    tool_decision: Dict[str, str]
    tool_output: str
    answer: str
    evaluation: Dict[str, float]
    final_response: Dict[str, object]
