from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings

from app.utils.config import settings


def get_llm(temperature: float = 0.2) -> ChatGoogleGenerativeAI:
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY is missing. Add it to your .env file.")

    return ChatGoogleGenerativeAI(
        model=settings.gemini_chat_model,
        google_api_key=settings.google_api_key,
        temperature=temperature,
         )


def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )