"""
Why this file exists:
    FastAPI should stay thin. ChatService contains the application logic for one
    chat turn.

Responsibility:
    - Run the LangGraph workflow.
    - Save the completed conversation to long-term memory.
    - Return data needed by the frontend.

How it connects to the project:
    The /chat endpoint calls ChatService.chat().
"""

from typing import Dict

from app.graph.workflow import ChatWorkflow
from app.knowledge_graph.kg_service import KnowledgeGraphService
from app.memory.memory_store import MemoryStore


class ChatService:
    """High-level chat service used by API routes."""

    def __init__(self) -> None:
        self.workflow = ChatWorkflow()
        self.memory_store = MemoryStore()
        self.kg_service = KnowledgeGraphService()

    def chat(self, user_id: str, message: str) -> Dict[str, object]:

        # ----------------------------------------------------------
        # Fast Greeting Shortcut (No RAG / No Gemini / No Neo4j)
        # ----------------------------------------------------------
        greetings = {
            "hi",
            "hello",
            "hey",
            "hii",
            "good morning",
            "good afternoon",
            "good evening",
            "how are you",
        }

        cleaned_message = message.lower().strip()

        if cleaned_message in greetings:
            answer = (
                "👋 Hello! Welcome to the Memory-Augmented Chatbot.\n\n"
                "I can help you with:\n"
                "• 📄 Questions from uploaded PDFs\n"
                "• 🧠 Long-term memory\n"
                "• 🕸️ Knowledge Graph facts\n"
                "• 🌦️ Weather\n"
                "• 🌐 Latest web information\n\n"
                "How can I help you today?"
            )

            self.memory_store.save_interaction(user_id, message, answer)

            return {
                "answer": answer,
                "memory": "",
                "graph_context": "",
                "retrieved_docs": [],
                "tool_output": "",
                "tool_decision": {},
                "evaluation": {
                    "groundedness": 1.0,
                    "faithfulness": 1.0,
                    "context_relevance": 1.0,
                    "answer_correctness": 1.0,
                },
            }

        # ----------------------------------------------------------
        # Normal LangGraph Workflow
        # ----------------------------------------------------------

        response = self.workflow.invoke(
            user_id=user_id,
            question=message,
        )

        answer = str(response.get("answer", ""))

        self.memory_store.save_interaction(
            user_id,
            message,
            answer,
        )

        # Store user facts inside Knowledge Graph
        self.kg_service.ingest_text(message)

        return response