import io
import pytest
from fastapi import UploadFile, HTTPException
from app.services.ingestion import IngestionService

def test_upload_file_valid():
    file_bytes = b"Hello, this is test content for ingestion validation."
    upload = UploadFile(filename="sample_test.txt", file=io.BytesIO(file_bytes))
    
    record = IngestionService.save_uploaded_file(upload)
    assert record["filename"] == "sample_test.txt"
    assert record["file_type"] == ".txt"
    assert record["status"] == "uploaded"
    assert record["file_size_bytes"] == len(file_bytes)

def test_upload_file_invalid_extension():
    file_bytes = b"echo 'bad script'"
    upload = UploadFile(filename="malicious.exe", file=io.BytesIO(file_bytes))
    
    with pytest.raises(HTTPException) as exc_info:
        IngestionService.save_uploaded_file(upload)
    assert exc_info.value.status_code == 400
