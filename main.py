
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

app = FastAPI(
    title="Memory-Augmented Chatbot with Knowledge Graph and Hybrid RAG",
    description="Free-tier Gemini + FAISS + Neo4j + LangGraph chatbot backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Memory-Augmented Chatbot API is running. Visit /docs for Swagger UI."}
