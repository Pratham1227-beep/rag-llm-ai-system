from app.services.okf import OKFService
from app.models.okf_schema import OKFDocument

def test_okf_creation_and_persistence():
    doc_id = "test_doc_123"
    filename = "report.pdf"
    file_size = 10240
    file_type = ".pdf"
    
    extracted_data = {
        "total_pages": 2,
        "pages": [
            {"page_number": 1, "text": "Page 1 intro", "has_ocr": False},
            {"page_number": 2, "text": "Page 2 conclusion", "has_ocr": False}
        ],
        "sections": [
            {"section_id": "sec_1", "title": "Introduction", "level": 1, "page_number": 1, "content": "Page 1 intro"}
        ],
        "tables": []
    }
    
    okf_doc = OKFService.create_okf_document(doc_id, filename, file_size, file_type, extracted_data)
    
    assert okf_doc.metadata.document_id == doc_id
    assert okf_doc.metadata.total_pages == 2
    assert len(okf_doc.sections) == 1
    
    # Reload from persistence
    reloaded = OKFService.load_okf_document(doc_id)
    assert reloaded is not None
    assert reloaded.metadata.filename == filename
    assert "Page 1 intro" in reloaded.get_full_text()
