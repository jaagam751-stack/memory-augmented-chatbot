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
