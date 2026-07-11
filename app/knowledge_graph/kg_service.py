from typing import Dict

from app.knowledge_graph.extractor import extract_knowledge_graph
from app.knowledge_graph.neo4j_graph import Neo4jGraphClient


class KnowledgeGraphService:
    """High-level knowledge graph service."""

    def __init__(self) -> None:
        self.client = Neo4jGraphClient()

    def ingest_text(self, text: str) -> Dict[str, int]:
        graph_data = extract_knowledge_graph(text)
        return self.client.store_graph(graph_data)

    def retrieve_context(self, question: str) -> str:
        return self.client.search_context(question)

    def status(self) -> Dict[str, object]:
        return self.client.status()
