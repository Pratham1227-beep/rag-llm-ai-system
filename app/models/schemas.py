from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Upload Schemas
class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_size_bytes: int
    upload_timestamp: str
    status: str
    message: str


# Processing Schemas
class DocumentProcessRequest(BaseModel):
    document_id: str
    chunk_size: int = Field(500, description="Target chunk character length")
    chunk_overlap: int = Field(50, description="Target chunk overlap length")
    enable_ocr: bool = Field(True, description="Enable OCR fallback for scanned pages")


class DocumentProcessResponse(BaseModel):
    document_id: str
    status: str
    sections_extracted: int
    tables_extracted: int
    total_chunks_indexed: int
    processing_time_seconds: float
    okf_saved: bool
    message: str


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    upload_timestamp: str
    file_size_bytes: int
    status: str
    total_pages: Optional[int] = None
    indexed_chunks: Optional[int] = None


# Retrieval & Citation Schemas
class SourceCitation(BaseModel):
    document_id: str
    filename: str
    page_number: int
    section_title: Optional[str] = None
    snippet: str
    relevance_score: float


class QueryRequest(BaseModel):
    query: str = Field(..., description="User query / question")
    top_k: int = Field(4, ge=1, le=20, description="Number of context chunks to retrieve")
    document_ids: Optional[List[str]] = Field(None, description="Filter search to specific document IDs")
    model: Optional[str] = Field(None, description="Override LLM model name")
    stream: bool = Field(False, description="Stream LLM response")


class QueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[SourceCitation]
    llm_model: str
    retrieval_count: int
    processing_time_seconds: float
    groundedness_score: Optional[float] = Field(None, description="Evaluation score of answer grounding")


# Health Check Schema
class HealthCheckResponse(BaseModel):
    status: str
    app_name: str
    vector_db_status: str
    ollama_status: str
    ollama_model: str
    timestamp: str
