

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.knowledge_graph.kg_service import KnowledgeGraphService
from app.memory.memory_store import MemoryStore
from app.rag.scraper import scrape_webpage
from app.rag.vector_store import VectorStoreManager
from app.services.chat_service import ChatService
from app.services.ingestion_service import IngestionService
from app.utils.config import settings

router = APIRouter()

# Services are created once and reused.
chat_service = ChatService()
memory_store = MemoryStore()
kg_service = KnowledgeGraphService()


class ChatRequest(BaseModel):
    user_id: str = Field(default="default_user", description="Unique user id for memory")
    message: str = Field(..., description="User message/question")


class ScrapeRequest(BaseModel):
    url: str
    ingest_after_scrape: bool = False


class IngestRequest(BaseModel):
    path: Optional[str] = None


@router.post("/chat")
def chat(request: ChatRequest):
    try:
        return chat_service.chat(user_id=request.user_id, message=request.message)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/scrape")
def scrape(request: ScrapeRequest):
    try:
        result = scrape_webpage(request.url)
        if request.ingest_after_scrape:
            ingestion_result = IngestionService().ingest(result["file_path"])
            result["ingestion"] = ingestion_result
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/ingest")
def ingest(request: IngestRequest):
    try:
        return IngestionService().ingest(path=request.path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/history")
def history(user_id: str = "default_user"):
    return {"user_id": user_id, "history": memory_store.history(user_id), "memory": memory_store.get_memory(user_id)}


@router.get("/health")
def health():
    vector_store = VectorStoreManager()
    return {
        "status": "ok",
        "google_api_key_set": settings.has_google_key(),
        "tavily_api_key_set": bool(settings.tavily_api_key),
        "openweather_api_key_set": bool(settings.openweather_api_key),
        "faiss_index_exists": vector_store.exists(),
        "knowledge_graph": kg_service.status(),
    }
