from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "ollama_connected" in data
    assert "vector_db_ready" in data
    assert "active_documents" in data

def test_upload_invalid_file_extension():
    response = client.post(
        "/documents/upload",
        files={"file": ("invalid_doc.txt", b"plain text content", "text/plain")}
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]

def test_upload_and_process_flow():
    # 1. Upload valid PDF
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    response = client.post(
        "/documents/upload",
        files={"file": ("sample_enterprise_doc.pdf", pdf_bytes, "application/pdf")}
    )
    assert response.status_code == 200
    upload_data = response.json()
    doc_id = upload_data["document_id"]
    assert upload_data["status"] == "uploaded"

    # 2. Process document
    process_resp = client.post(
        "/documents/process",
        json={"document_id": doc_id, "chunk_size": 300, "chunk_overlap": 30, "force_ocr": False}
    )
    assert process_resp.status_code == 200
    process_data = process_resp.json()
    assert process_data["status"] == "indexed"

    # 3. List documents
    list_resp = client.get("/documents")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 1

    # 4. Get document detail & OKF representation
    doc_detail_resp = client.get(f"/documents/{doc_id}")
    assert doc_detail_resp.status_code == 200
    detail_data = doc_detail_resp.json()
    assert detail_data["metadata"]["document_id"] == doc_id
    assert detail_data["okf"] is not None

    # 5. Query RAG system
    query_resp = client.post(
        "/query",
        json={
            "prompt": "What is the document context?",
            "top_k": 2,
            "filters": {"document_ids": [doc_id]}
        }
    )
    assert query_resp.status_code == 200
    query_data = query_resp.json()
    assert "query" in query_data
    assert "answer" in query_data
    assert "citations" in query_data
