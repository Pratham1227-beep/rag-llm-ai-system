import logging
from typing import List
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    _model = None

    @classmethod
    def _get_model(cls):
        if cls._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
                try:
                    cls._model = SentenceTransformer(
                        settings.EMBEDDING_MODEL_NAME,
                        device="cpu",
                        model_kwargs={"low_cpu_mem_usage": False}
                    )
                except Exception as inner_e:
                    logger.warning(f"First load attempt failed ({inner_e}), trying standard cpu load...")
                    cls._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME, device="cpu")
            except Exception as e:
                logger.error(f"Failed to load SentenceTransformer model ({e}). Using CPU fallback/mock mode if needed.")
                cls._model = None
        return cls._model

    @classmethod
    def embed_texts(cls, texts: List[str]) -> List[List[float]]:
        model = cls._get_model()
        if model is not None:
            embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            return embeddings.tolist()
        else:
            # Deterministic mock fallback for lightweight environments without model download
            logger.warning("Using mock embedding generator (SentenceTransformer unavailable).")
            embeddings = []
            for text in texts:
                # Generate pseudo-embedding vector of size 384
                import hashlib
                h = hashlib.sha256(text.encode("utf-8")).digest()
                vector = [(float(b) / 255.0) * 2 - 1 for b in (h * 12)[:384]]
                embeddings.append(vector)
            return embeddings

    @classmethod
    def embed_query(cls, query: str) -> List[float]:
        return cls.embed_texts([query])[0]
