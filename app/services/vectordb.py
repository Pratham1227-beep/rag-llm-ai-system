import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings
from app.services.embeddings import EmbeddingService

logger = logging.getLogger(__name__)

class VectorDBService:
    _client = None
    _collection = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            settings.ensure_directories()
            cls._client = chromadb.PersistentClient(
                path=settings.VECTOR_DB_DIR,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
        return cls._client

    @classmethod
    def get_collection(cls):
        if cls._collection is None:
            client = cls.get_client()
            cls._collection = client.get_or_create_collection(
                name="rag_chunks",
                metadata={"hnsw:space": "cosine"}
            )
        return cls._collection

    @classmethod
    def add_chunks(cls, chunks: List[Dict[str, Any]]) -> int:
        if not chunks:
            return 0

        collection = cls.get_collection()

        ids = [c["chunk_id"] for c in chunks]
        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        # Generate embeddings
        embeddings = EmbeddingService.embed_texts(texts)

        # Upsert into ChromaDB
        collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        return len(chunks)

    @classmethod
    def similarity_search(
        cls,
        query: str,
        top_k: int = 4,
        document_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        collection = cls.get_collection()
        query_vector = EmbeddingService.embed_query(query)

        where_clause = None
        if document_ids:
            if len(document_ids) == 1:
                where_clause = {"document_id": document_ids[0]}
            else:
                where_clause = {"document_id": {"$in": document_ids}}

        results = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )

        search_results = []
        if results and results.get("documents") and len(results["documents"]) > 0:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            dists = results["distances"][0]

            for doc, meta, dist in zip(docs, metas, dists):
                # Cosine distance to similarity conversion
                similarity = max(0.0, min(1.0, 1.0 - dist))
                search_results.append({
                    "chunk_id": meta.get("chunk_id", ""),
                    "document_id": meta.get("document_id", ""),
                    "filename": meta.get("filename", "Unknown"),
                    "page_number": int(meta.get("page_number", 1)),
                    "section_title": meta.get("section_title", "General"),
                    "snippet": doc,
                    "relevance_score": round(similarity, 4)
                })

        return search_results

    @classmethod
    def get_status(cls) -> str:
        try:
            col = cls.get_collection()
            count = col.count()
            return f"ready ({count} indexed chunks)"
        except Exception as e:
            return f"error: {str(e)}"
