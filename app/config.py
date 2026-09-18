import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Enterprise RAG + LLM AI System"
    DEBUG: bool = True
    PORT: int = 8000

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    OLLAMA_TIMEOUT_SECONDS: float = 60.0

    VECTOR_DB_DIR: str = "./data/vector_db"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    TOP_K_RETRIEVAL: int = 4

    UPLOAD_DIR: str = "./data/uploads"
    OKF_STORE_DIR: str = "./data/okf_store"
    MAX_UPLOAD_SIZE_MB: int = 25

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

    def ensure_directories(self):
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.OKF_STORE_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.VECTOR_DB_DIR).mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()
