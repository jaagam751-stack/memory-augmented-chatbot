"""
Why this file exists:
    Ingestion is the bridge between scraped/local documents and the chatbot's
    retrieval systems.

Responsibility:
    - Load documents.
    - Chunk documents.
    -Store chunks in FAISS using Hugging Face Sentence Transformer embeddings.
    - Extract/store knowledge graph data in Neo4j.

How it connects to the project:
    The /ingest API endpoint calls this service after scraping or when ingesting
    existing files from data/documents/.
"""

from typing import Dict, Optional

from app.knowledge_graph.kg_service import KnowledgeGraphService
from app.rag.document_loader import chunk_documents, load_documents
from app.rag.vector_store import VectorStoreManager


class IngestionService:
    """Runs the full ingestion pipeline."""

    def __init__(self) -> None:
        self.vector_store = VectorStoreManager()
        self.kg_service = KnowledgeGraphService()

    def ingest(self, path: Optional[str] = None) -> Dict[str, object]:
        documents = load_documents(path)
        chunks = chunk_documents(documents)
        vector_count = self.vector_store.build_or_update(chunks)

        kg_entities = 0
        kg_relationships = 0
        for doc in documents:
            stats = self.kg_service.ingest_text(doc.page_content)
            kg_entities += stats.get("entities", 0)
            kg_relationships += stats.get("relationships", 0)

        return {
            "documents_loaded": len(documents),
            "chunks_indexed": vector_count,
            "kg_entities_added": kg_entities,
            "kg_relationships_added": kg_relationships,
        }
