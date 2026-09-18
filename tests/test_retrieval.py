from app.services.okf import OKFService
from app.services.chunking import DocumentChunker
from app.services.vectordb import VectorDBService

def test_chunking_and_vector_indexing():
    extracted_data = {
        "total_pages": 1,
        "pages": [
            {"page_number": 1, "text": "Enterprise RAG systems leverage vector databases such as ChromaDB for fast similarity retrieval.", "has_ocr": False}
        ],
        "sections": [
            {"section_id": "sec_1", "title": "Overview", "level": 1, "page_number": 1, "content": ""}
        ],
        "tables": []
    }
    
    doc_id = "test_retrieval_doc"
    okf_doc = OKFService.create_okf_document(doc_id, "guide.txt", 500, ".txt", extracted_data)
    
    chunks = DocumentChunker.chunk_okf_document(okf_doc, chunk_size=200, chunk_overlap=20)
    assert len(chunks) > 0
    assert chunks[0]["document_id"] == doc_id
    
    indexed_count = VectorDBService.add_chunks(chunks)
    assert indexed_count == len(chunks)
    
    # Test similarity search
    results = VectorDBService.similarity_search(query="vector databases ChromaDB", top_k=2, document_ids=[doc_id])
    assert len(results) > 0
    assert results[0]["document_id"] == doc_id
    assert "ChromaDB" in results[0]["snippet"]
