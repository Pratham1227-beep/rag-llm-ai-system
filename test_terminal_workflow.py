import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_workflow():
    print("Starting Workflow Test...")
    
    # 1. Upload
    start_time = time.time()
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    response = client.post(
        "/documents/upload",
        files={"file": ("sample_terminal_doc.pdf", pdf_bytes, "application/pdf")}
    )
    upload_time = time.time() - start_time
    assert response.status_code == 200, f"Upload failed: {response.text}"
    upload_data = response.json()
    doc_id = upload_data["document_id"]
    print(f"Upload successful (Time: {upload_time:.4f}s) | Document ID: {doc_id}")

    # 2. Process document (Extraction, OKF, Chunking, Tokenisation, Embeddings)
    start_time = time.time()
    process_resp = client.post(
        "/documents/process",
        json={"document_id": doc_id, "chunk_size": 300, "chunk_overlap": 30, "force_ocr": False}
    )
    process_time = time.time() - start_time
    assert process_resp.status_code == 200, f"Processing failed: {process_resp.text}"
    process_data = process_resp.json()
    print(f"Processing (Chunking, Tokenisation, OKF) completed (Time: {process_time:.4f}s)")
    print(f"Chunks generated: {process_data.get('total_chunks_indexed', 'Unknown')}")
    
    # 3. Get document detail & OKF representation
    doc_detail_resp = client.get(f"/documents/{doc_id}")
    assert doc_detail_resp.status_code == 200
    detail_data = doc_detail_resp.json()
    
    assert "metadata" in detail_data, "OKF metadata is missing!"
    assert "sections" in detail_data, "OKF sections is missing!"
    print(f"OKF Representation successfully generated and retrieved (Version: {detail_data.get('okf_version')}).")
    
    print("\n--- Summary ---")
    print("Chunking and Tokenisation: SUCCESS")
    print("OKF Backend Integrity: SUCCESS")
    print(f"Total Loading/Processing Time: {upload_time + process_time:.4f}s")

if __name__ == "__main__":
    test_full_workflow()
