"""
Why this file exists:
    This is the core LangGraph agent workflow required by the assignment.

Responsibility:
    - Create graph nodes: Input, Memory Retrieval, Hybrid RAG, Knowledge Graph,
      Tool Calling, LLM, Evaluation, and Response.
    - Use conditional routing to call tools only when needed.
    - Return a complete response object for FastAPI and Streamlit.

How it connects to the project:
    ChatService invokes this compiled graph for every /chat request.
"""

from typing import Dict

from langgraph.graph import END, StateGraph

from app.evaluation.evaluator import Evaluator
from app.graph.state import AgentState
from app.knowledge_graph.kg_service import KnowledgeGraphService
from app.memory.memory_store import MemoryStore
from app.prompts.prompts import ANSWER_PROMPT
from app.rag.hybrid_retriever import HybridRetriever
from app.tools.tool_router import ToolRouter
from app.utils.gemini import get_llm


class ChatWorkflow:
    """Builds and runs the LangGraph workflow."""

    def __init__(self) -> None:
        self.memory_store = MemoryStore()
        self.hybrid_retriever = HybridRetriever()
        self.kg_service = KnowledgeGraphService()
        self.tool_router = ToolRouter()
        self.evaluator = Evaluator()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("input", self.input_node)
        workflow.add_node("memory_retrieval", self.memory_retrieval_node)
        workflow.add_node("hybrid_rag", self.hybrid_rag_node)
        workflow.add_node("knowledge_graph", self.knowledge_graph_node)
        workflow.add_node("tool_decision", self.tool_decision_node)
        workflow.add_node("tool_calling", self.tool_calling_node)
        workflow.add_node("llm", self.llm_node)
        workflow.add_node("evaluation", self.evaluation_node)
        workflow.add_node("response", self.response_node)

        workflow.set_entry_point("input")
        workflow.add_edge("input", "memory_retrieval")
        workflow.add_edge("memory_retrieval", "hybrid_rag")
        workflow.add_edge("hybrid_rag", "knowledge_graph")
        workflow.add_edge("knowledge_graph", "tool_decision")

        # Conditional routing: only call a tool if the decision says so.
        workflow.add_conditional_edges(
            "tool_decision",
            self.should_call_tool,
            {"call_tool": "tool_calling", "skip_tool": "llm"},
        )
        workflow.add_edge("tool_calling", "llm")
        workflow.add_edge("llm", "evaluation")
        workflow.add_edge("evaluation", "response")
        workflow.add_edge("response", END)

        return workflow.compile()

    def input_node(self, state: AgentState) -> AgentState:
        """Input node: normalize required state fields."""
        return {
            "user_id": state.get("user_id", "default_user"),
            "question": state.get("question", ""),
        }

    def memory_retrieval_node(self, state: AgentState) -> AgentState:
        """Memory Retrieval node: fetch long-term memory."""
        user_id = state.get("user_id", "default_user")
        question = state.get("question", "")
        self.memory_store.update_from_user_message(user_id, question)
        return {"memory": self.memory_store.memory_as_text(user_id)}

    def hybrid_rag_node(self, state: AgentState) -> AgentState:
        """Hybrid RAG node: retrieve FAISS chunks and graph facts."""
        result = self.hybrid_retriever.retrieve(state.get("question", ""))
        return {
            "context": result["context"],
            "retrieved_docs": result["documents"],
            "graph_context": result["graph_context"],
        }

    def knowledge_graph_node(self, state: AgentState) -> AgentState:
        """Knowledge Graph node: refresh graph context from Neo4j."""
        graph_context = self.kg_service.retrieve_context(state.get("question", ""))
        return {"graph_context": graph_context}

    def tool_decision_node(self, state: AgentState) -> AgentState:
        """Tool decision node: choose Tavily, Weather, or none."""
        decision = self.tool_router.decide(state.get("question", ""))
        return {"tool_decision": decision}

    def should_call_tool(self, state: AgentState) -> str:
        """Conditional route used by LangGraph."""
        if state.get("tool_decision", {}).get("tool") in {"tavily_search", "weather"}:
            return "call_tool"
        return "skip_tool"

    def tool_calling_node(self, state: AgentState) -> AgentState:
        """Tool Calling node: run the selected external tool."""
        result = self.tool_router.run(state.get("tool_decision", {}))
        return {"tool_output": result.get("output", "")}

    def llm_node(self, state: AgentState) -> AgentState:

        """LLM node: ask Gemini to produce the final answer."""
        prompt = ANSWER_PROMPT.format(
            memory=state.get("memory", ""),
            context=state.get("context", ""),
            graph_context=state.get("graph_context", ""),
            tool_output=state.get("tool_output", "No tool output."),
            question=state.get("question", ""),
        )

        try:
            llm = get_llm(temperature=0.2)
            response = llm.invoke(prompt)

   
            raw_content = response.content
            if isinstance(raw_content, list):
                answer_text = "".join(
                    block.get("text", "") if isinstance(block, dict) else str(block)
                    for block in raw_content
                )
            else:
                answer_text = str(raw_content)

            return {"answer": answer_text}

        except Exception as e:
            error = str(e)

            if "RESOURCE_EXHAUSTED" in error or "429" in error:
                return {
                    "answer": (
                        "⚠️ Gemini free API quota exceeded.\n\n"
                        "Please wait a minute or use another Google API key."
                   )
                }

            return {
                "answer": f"⚠️ LLM Error:\n{error}"
            }
    # def llm_node(self, state: AgentState) -> AgentState:
        
    #         """LLM node: ask Gemini to produce the final answer."""
    #         prompt = ANSWER_PROMPT.format(
    #             memory=state.get("memory", ""),
    #             context=state.get("context", ""),
    #             graph_context=state.get("graph_context", ""),
    #             tool_output=state.get("tool_output", "No tool output."),
    #             question=state.get("question", ""),
    #         )

    #         try:
    #             llm = get_llm(temperature=0.2)
    #             response = llm.invoke(prompt)
    #             return {
    #                  "answer": response.content
    #             }

    #         except Exception as e:
    #             error = str(e)

    #             if "RESOURCE_EXHAUSTED" in error or "429" in error:
    #                 return {
    #                     "answer": (
    #                         "⚠️ Gemini free API quota exceeded.\n\n"
    #                         "Please wait a minute or use another Google API key."
    #                    )
    #                 }

    #             return {
    #                 "answer": f"⚠️ LLM Error:\n{error}"
    #             }
  

    def evaluation_node(self, state: AgentState) -> AgentState:
        """Evaluation node: score the generated answer."""
        scores = self.evaluator.evaluate(
            question=state.get("question", ""),
            answer=state.get("answer", ""),
            context=state.get("context", "") + "\n" + state.get("tool_output", ""),
        )
        return {"evaluation": scores}

    def response_node(self, state: AgentState) -> AgentState:
        """Response node: package data for API/UI."""
        final_response: Dict[str, object] = {
            "answer": state.get("answer", ""),
            "memory": state.get("memory", ""),
            "retrieved_docs": state.get("retrieved_docs", []),
            "graph_context": state.get("graph_context", ""),
            "tool_decision": state.get("tool_decision", {}),
            "tool_output": state.get("tool_output", ""),
            "evaluation": state.get("evaluation", {}),
        }
        return {"final_response": final_response}

    def invoke(self, user_id: str, question: str) -> Dict[str, object]:
        """Run the compiled LangGraph app."""
        result = self.graph.invoke({"user_id": user_id, "question": question})
        return result.get("final_response", {})
