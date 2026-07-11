"""
Why this file exists:
    FAISS cannot index raw files directly. Documents must be loaded and split into
    smaller chunks first.

Responsibility:
    - Read PDF, TXT and Markdown files.
    - Support both a single file and an entire folder.
    - Convert them into LangChain Documents.
    - Split them into chunks.

How it connects:
    IngestionService -> load_documents() -> chunk_documents() -> FAISS
"""

from pathlib import Path
from typing import List, Optional

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from app.utils.config import settings


def load_documents(path: Optional[str] = None) -> List[Document]:
    docs: List[Document] = []

    if path:
        target = Path(path)

        if target.is_dir():
            files = (
                list(target.glob("*.pdf"))
                + list(target.glob("*.txt"))
                + list(target.glob("*.md"))
            )
        else:
            files = [target]
    else:
        files = (
            list(settings.documents_dir.glob("*.pdf"))
            + list(settings.documents_dir.glob("*.txt"))
            + list(settings.documents_dir.glob("*.md"))
        )

    for file_path in files:

        if not file_path.exists():
            continue

        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            loader = PyPDFLoader(str(file_path))
            docs.extend(loader.load())

        elif suffix in [".txt", ".md"]:
            text = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            docs.append(
                Document(
                    page_content=text,
                    metadata={"source": str(file_path)},
                )
            )

    return docs


def chunk_documents(
    documents: List[Document],
    chunk_size: int = 900,
    chunk_overlap: int = 150,
) -> List[Document]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    return splitter.split_documents(documents)