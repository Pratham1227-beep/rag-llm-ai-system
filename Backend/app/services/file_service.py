import PyPDF2
from io import BytesIO
import uuid
from app.services import vector_service

def extract_pages_from_pdf(pdf_bytes):
    """Extract text page-by-page from PDF bytes without limits."""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes), strict=False)
        total_pages = len(pdf_reader.pages)
        pages_data = []
        for idx, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    pages_data.append({
                        "page": idx + 1,
                        "text": page_text.strip()
                    })
            except Exception:
                continue
        return pages_data, total_pages
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

def chunk_document(filename, pages_data, chunk_size=800, chunk_overlap=150):
    """
    Splits document pages into semantic chunks with overlap for Vector Database indexing.
    Tracks document name, page number, and chunk index in metadata.
    """
    chunks = []
    chunk_index = 0
    
    for page_info in pages_data:
        page_num = page_info["page"]
        text = page_info["text"]
        
        if not text:
            continue
            
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk_content = text[start:end].strip()
            
            if chunk_content:
                chunk_id = f"{filename}_p{page_num}_c{chunk_index}_{uuid.uuid4().hex[:6]}"
                chunks.append({
                    "id": chunk_id,
                    "text": chunk_content,
                    "metadata": {
                        "source": filename,
                        "page": page_num,
                        "chunk_index": chunk_index
                    }
                })
                chunk_index += 1
                
            if end >= text_len:
                break
            start += chunk_size - chunk_overlap
            
    return chunks

def process_uploaded_file(file):
    """
    Route file, extract full text across all pages, split into chunks,
    and index them into the ChromaDB Vector Database.
    """
    filename = file.filename
    file_bytes = file.read()
    
    if filename.lower().endswith('.pdf'):
        pages_data, total_pages = extract_pages_from_pdf(file_bytes)
        full_text = "\n\n".join([f"[Page {p['page']} of {total_pages}]\n{p['text']}" for p in pages_data])
    elif filename.lower().endswith('.txt'):
        text = file_bytes.decode('utf-8', errors='ignore')
        total_pages = 1
        pages_data = [{"page": 1, "text": text}]
        full_text = text
    else:
        raise ValueError(f"Unsupported file type: {filename}")
        
    # 1. Chunk document
    chunks = chunk_document(filename, pages_data, chunk_size=800, chunk_overlap=150)
    
    # 2. Ingest into ChromaDB Vector Database
    db_result = vector_service.add_chunks_to_vector_db(chunks)
    
    return {
        "name": filename,
        "content": full_text,
        "size": len(file_bytes),
        "type": file.content_type,
        "total_pages": total_pages,
        "chunks_created": len(chunks),
        "vector_db_status": "indexed",
        "total_chunks_in_db": db_result["total_chunks_in_db"]
    }