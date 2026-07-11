"""
Why this file exists:
    Hybrid RAG requires semantic retrieval. FAISS stores embeddings locally and
    searches for chunks similar to the user's question.

Responsibility:
    - Build a FAISS vector index with Gemini embeddings.
    - Save and load the index from vectorstore/.
    - Search relevant document chunks.

How it connects to the project:
    Ingestion writes to FAISS. The LangGraph Hybrid RAG node reads from FAISS to
    retrieve context for Gemini.
"""

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from app.utils.config import settings
from app.utils.gemini import get_embeddings


class VectorStoreManager:
    """Small wrapper around LangChain FAISS."""

    def __init__(self) -> None:
        self.index_path: Path = settings.vectorstore_dir / settings.faiss_index_name

    def _embeddings(self):
        """Create embeddings lazily so /health can work even before keys are added."""
        return get_embeddings()

    def exists(self) -> bool:
        """Check whether a saved FAISS index exists."""
        return (self.index_path / "index.faiss").exists()

    def load(self) -> FAISS:
        """Load an existing FAISS index from disk."""
        return FAISS.load_local(
            folder_path=str(self.index_path),
            embeddings=self._embeddings(),
            allow_dangerous_deserialization=True,
        )

    def build_or_update(self, documents: List[Document]) -> int:
        """Create a new FAISS index or add documents to the existing one."""
        if not documents:
            return 0

        if self.exists():
            vectorstore = self.load()
            vectorstore.add_documents(documents)
        else:
            vectorstore = FAISS.from_documents(documents, self._embeddings())

        vectorstore.save_local(str(self.index_path))
        return len(documents)

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Return the top-k semantically similar chunks."""
        if not self.exists():
            return []
        vectorstore = self.load()
        return vectorstore.similarity_search(query, k=k)
