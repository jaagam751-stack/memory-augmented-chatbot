from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    tavily_api_key: Optional[str] = Field(default=None, alias="TAVILY_API_KEY")
    openweather_api_key: Optional[str] = Field(default=None, alias="OPENWEATHER_API_KEY")

    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_username: str = Field(default="neo4j", alias="NEO4J_USERNAME")
    neo4j_password: str = Field(default="password", alias="NEO4J_PASSWORD")

    project_root: Path = Path(__file__).resolve().parents[2]
    data_dir: Path = project_root / "data"
    documents_dir: Path = data_dir / "documents"
    memory_file: Path = data_dir / "memory.json"
    vectorstore_dir: Path = project_root / "vectorstore"
    faiss_index_name: str = "faiss_index"

    gemini_chat_model: str = "gemini-3.5-flash"

    class Config:
        populate_by_name = True
        extra = "ignore"

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        self.vectorstore_dir.mkdir(parents=True, exist_ok=True)

    def has_google_key(self) -> bool:
        return bool(self.google_api_key)


settings = Settings()
settings.ensure_directories()