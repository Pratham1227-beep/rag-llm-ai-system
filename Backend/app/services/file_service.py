from io import BytesIO
import uuid
import os
from app.services import vector_service

def extract_pages_from_pdf(pdf_bytes):
    """
    Extract text page-by-page from PDF bytes.
    Uses PyMuPDF (fitz) as the primary extractor for speed, font support,
    and multi-page reliability, with fallbacks to pypdf / PyPDF2.
    """
    pages_data = []
    total_pages = 0

    # 1. Primary engine: PyMuPDF (fitz) - industry standard, fast & robust
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(doc)
        for idx, page in enumerate(doc):
            try:
                page_text = page.get_text("text")
                if page_text and page_text.strip():
                    pages_data.append({
                        "page": idx + 1,
                        "text": page_text.strip()
                    })
            except Exception:
                continue
        doc.close()
    except Exception:
        pages_data = []

    # 2. Fallback engine: pypdf / PyPDF2 if fitz produced no pages
    if not pages_data:
        try:
            import pypdf
            reader = pypdf.PdfReader(BytesIO(pdf_bytes), strict=False)
            total_pages = len(reader.pages)
            for idx, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        pages_data.append({
                            "page": idx + 1,
                            "text": text.strip()
                        })
                except Exception:
                    continue
        except Exception:
            pass

    # 3. Third fallback: PyPDF2
    if not pages_data:
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(BytesIO(pdf_bytes), strict=False)
            total_pages = len(reader.pages)
            for idx, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        pages_data.append({
                            "page": idx + 1,
                            "text": text.strip()
                        })
                except Exception:
                    continue
        except Exception:
            pass

    # If completely empty (e.g. scanned image-only PDF), ensure at least 1 page representation
    if not pages_data:
        total_pages = max(1, total_pages)
        pages_data.append({
            "page": 1,
            "text": "[Scanned or image-based PDF: Text could not be extracted directly from this document.]"
        })

    return pages_data, total_pages

def chunk_document(filename, pages_data, chunk_size=1200, chunk_overlap=200):
    """
    Splits document pages into semantic chunks with overlap for Vector Database indexing.
    Tracks document name, page number, and chunk index in metadata.
    """
    chunks = []
    chunk_index = 0
    
    for page_info in pages_data:
        page_num = page_info["page"]
        text = page_info["text"]
        
        if not text or not text.strip():
            continue
            
        start = 0
        text_len = len(text)
        
        # If page text is shorter than chunk_size, create one chunk for the page
        if text_len <= chunk_size:
            chunk_id = f"{filename}_p{page_num}_c{chunk_index}_{uuid.uuid4().hex[:6]}"
            chunks.append({
                "id": chunk_id,
                "text": text.strip(),
                "metadata": {
                    "source": filename,
                    "page": page_num,
                    "chunk_index": chunk_index
                }
            })
            chunk_index += 1
            continue

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
            start += max(1, chunk_size - chunk_overlap)
            
    return chunks

def process_uploaded_file(file):
    """
    Route file, extract full text across all pages using PyMuPDF,
    split into semantic chunks, and index them into ChromaDB Vector Database.
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
    chunks = chunk_document(filename, pages_data, chunk_size=1200, chunk_overlap=200)
    
    # 2. Ingest into ChromaDB Vector Database
    db_result = vector_service.add_chunks_to_vector_db(chunks)
    
    total_in_db = db_result.get("total_chunks_in_db", 0)
    
    return {
        "name": filename,
        "content": full_text,
        "size": len(file_bytes),
        "type": file.content_type,
        "total_pages": total_pages,
        "chunks_created": len(chunks),
        "vector_db_status": "indexed",
        "total_chunks_in_db": total_in_db
    }