import os
import chromadb
from chromadb.config import Settings

# Persistent ChromaDB storage path inside the Backend directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHROMA_DATA_DIR = os.path.join(BASE_DIR, 'chroma_db')
os.makedirs(CHROMA_DATA_DIR, exist_ok=True)

COLLECTION_NAME = "enterprise_rag_chunks"

def get_chroma_client():
    """Initializes and returns a persistent ChromaDB client."""
    return chromadb.PersistentClient(path=CHROMA_DATA_DIR)

def get_collection():
    """Retrieves or creates the vector collection configured for cosine similarity."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

def add_chunks_to_vector_db(chunks):
    """
    Ingests a list of chunk dictionaries into the ChromaDB vector database.
    Each chunk dict must have:
      - 'id': unique string id
      - 'text': text content of the chunk
      - 'metadata': dict with 'source', 'page', 'chunk_index'
    """
    collection = get_collection()
    
    if not chunks:
        return {
            "chunks_added": 0,
            "total_chunks_in_db": collection.count()
        }

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        ids.append(str(chunk['id']))
        documents.append(str(chunk['text']))
        # ChromaDB metadata values must be primitive types (str, int, float, bool)
        meta = {
            "source": str(chunk.get('metadata', {}).get('source', 'Unknown')),
            "page": int(chunk.get('metadata', {}).get('page', 1)),
            "chunk_index": int(chunk.get('metadata', {}).get('chunk_index', 0))
        }
        metadatas.append(meta)

    # Ingest using upsert in safe batches to prevent duplicates or size limits
    batch_size = 40
    for i in range(0, len(ids), batch_size):
        collection.upsert(
            ids=ids[i:i + batch_size],
            documents=documents[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size]
        )

    return {
        "chunks_added": len(chunks),
        "total_chunks_in_db": collection.count()
    }

def search_relevant_chunks(query, top_k=6, source_filter=None):
    """
    Performs semantic vector similarity search in ChromaDB.
    Returns the top-k most relevant text chunks along with metadata and relevance scores.
    """
    collection = get_collection()
    total_docs = collection.count()

    if total_docs == 0:
        return []

    query_params = {
        "query_texts": [query],
        "n_results": min(top_k, total_docs)
    }

    if source_filter:
        query_params["where"] = {"source": source_filter}

    results = collection.query(**query_params)

    retrieved = []
    if results and 'documents' in results and results['documents']:
        docs = results['documents'][0]
        metas = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else [{}] * len(docs)
        distances = results['distances'][0] if 'distances' in results and results['distances'] else [0.0] * len(docs)
        ids = results['ids'][0] if 'ids' in results and results['ids'] else [''] * len(docs)

        for doc_text, meta, dist, chunk_id in zip(docs, metas, distances, ids):
            # For cosine distance: 0.0 is exact match, 1.0 is orthogonal, 2.0 is opposite
            similarity_pct = max(0, min(100, int((1.0 - (dist / 2.0)) * 100)))
            retrieved.append({
                "id": chunk_id,
                "text": doc_text,
                "source": meta.get("source", "Unknown Document"),
                "page": meta.get("page", 1),
                "chunk_index": meta.get("chunk_index", 0),
                "distance": dist,
                "similarity_score": f"{similarity_pct}%"
            })

    return retrieved

def get_vector_db_stats():
    """Returns statistics about the vector database contents."""
    collection = get_collection()
    total = collection.count()
    
    unique_sources = set()
    if total > 0:
        # Fetch metadata to determine unique document sources
        try:
            sample = collection.get(limit=min(total, 5000), include=["metadatas"])
            if sample and "metadatas" in sample:
                for meta in sample["metadatas"]:
                    if meta and "source" in meta:
                        unique_sources.add(meta["source"])
        except Exception:
            pass

    return {
        "status": "ready",
        "total_chunks": total,
        "total_documents": len(unique_sources),
        "document_names": list(unique_sources),
        "storage_path": CHROMA_DATA_DIR
    }

def clear_vector_db():
    """Clears all vectors and chunks from ChromaDB."""
    client = get_chroma_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    # Recreate fresh collection
    client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    return {"status": "cleared", "total_chunks": 0}
