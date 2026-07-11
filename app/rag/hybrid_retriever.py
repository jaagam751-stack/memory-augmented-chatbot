"""
Why this file exists:
    Hybrid RAG means we do not rely on only one retrieval method. We combine
    semantic vector search with Knowledge Graph facts.

Responsibility:
    - Retrieve document chunks from FAISS.
    - Retrieve related graph facts from Neo4j.
    - Merge both into one context string for Gemini.

How it connects to the project:
    The LangGraph Hybrid RAG node calls this class for every chat request.
"""

from typing import Dict, List

from langchain_core.documents import Document

from app.knowledge_graph.kg_service import KnowledgeGraphService
from app.rag.vector_store import VectorStoreManager


class HybridRetriever:
    """Combines FAISS semantic search and Neo4j graph retrieval."""

    def __init__(self) -> None:
        self.vector_store = VectorStoreManager()
        self.kg_service = KnowledgeGraphService()

    def retrieve(self, question: str, k: int = 4) -> Dict[str, object]:
        docs: List[Document] = self.vector_store.similarity_search(question, k=k)
        semantic_context = "\n\n".join(
            f"Source: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
            for doc in docs
        )
        graph_context = self.kg_service.retrieve_context(question)

        merged_context = f"Semantic document context:\n{semantic_context or 'No matching documents found.'}\n\nGraph facts:\n{graph_context}"

        return {
            "context": merged_context,
            "documents": [
                {
                    "source": doc.metadata.get("source", "unknown"),
                    "preview": doc.page_content[:400],
                }
                for doc in docs
            ],
            "graph_context": graph_context,
        }
