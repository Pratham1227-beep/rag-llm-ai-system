import time
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from app.models.schemas import (
    DocumentUploadResponse, DocumentProcessRequest, DocumentProcessResponse, DocumentInfo
)
from app.models.okf_schema import OKFDocument
from app.services.ingestion import IngestionService
from app.services.extraction import ExtractionService
from app.services.okf import OKFService
from app.services.chunking import DocumentChunker
from app.services.vectordb import VectorDBService

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentUploadResponse)
def upload_document(file: UploadFile = File(...)):
    record = IngestionService.save_uploaded_file(file)
    return DocumentUploadResponse(
        document_id=record["document_id"],
        filename=record["filename"],
        file_size_bytes=record["file_size_bytes"],
        upload_timestamp=record["upload_timestamp"],
        status=record["status"],
        message="Document uploaded successfully and ready for processing."
    )

@router.post("/process", response_model=DocumentProcessResponse)
def process_document(req: DocumentProcessRequest):
    start_time = time.time()
    
    doc = IngestionService.get_document(req.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document with ID '{req.document_id}' not found.")

    file_path = doc["file_path"]

    try:
        # 1. Extraction
        extracted_data = ExtractionService.extract_document(file_path, enable_ocr=req.enable_ocr)

        # 2. OKF Conversion & Storage
        okf_doc = OKFService.create_okf_document(
            doc_id=req.document_id,
            filename=doc["filename"],
            file_size_bytes=doc["file_size_bytes"],
            file_type=doc["file_type"],
            extracted_data=extracted_data
        )

        # 3. Chunking
        chunks = DocumentChunker.chunk_okf_document(
            okf_doc,
            chunk_size=req.chunk_size,
            chunk_overlap=req.chunk_overlap
        )

        # 4. Vector Database Indexing
        indexed_count = VectorDBService.add_chunks(chunks)

        # Update registry status
        processing_time = round(time.time() - start_time, 2)
        IngestionService.update_status(
            req.document_id,
            status="processed",
            extra_meta={
                "total_pages": okf_doc.metadata.total_pages,
                "indexed_chunks": indexed_count,
                "processing_time_seconds": processing_time
            }
        )

        return DocumentProcessResponse(
            document_id=req.document_id,
            status="processed",
            sections_extracted=len(okf_doc.sections),
            tables_extracted=len(okf_doc.tables),
            total_chunks_indexed=indexed_count,
            processing_time_seconds=processing_time,
            okf_saved=True,
            message="Document successfully processed, converted to OKF, and indexed in Vector DB."
        )
    except Exception as e:
        IngestionService.update_status(req.document_id, status="failed", extra_meta={"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@router.get("", response_model=List[DocumentInfo])
def list_documents():
    docs = IngestionService.list_documents()
    res = []
    for d in docs:
        res.append(DocumentInfo(
            document_id=d["document_id"],
            filename=d["filename"],
            upload_timestamp=d["upload_timestamp"],
            file_size_bytes=d["file_size_bytes"],
            status=d.get("status", "unknown"),
            total_pages=d.get("total_pages"),
            indexed_chunks=d.get("indexed_chunks")
        ))
    return res

@router.get("/{document_id}", response_model=OKFDocument)
def get_document_okf(document_id: str):
    okf_doc = OKFService.load_okf_document(document_id)
    if not okf_doc:
        raise HTTPException(status_code=404, detail=f"OKF record for document '{document_id}' not found.")
    return okf_doc
