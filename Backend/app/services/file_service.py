from io import BytesIO
import uuid
from app.services import vector_service

def extract_pages_from_pdf(pdf_bytes):
    """
    Extracts complete, un-truncated text from every single page of the PDF.
    Uses PyMuPDF (fitz) for maximum fidelity and completeness.
    """
    pages_data = []
    total_pages = 0

    # 1. Primary: PyMuPDF (fitz) extracts all text, blocks, and formatting
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(doc)
        for idx in range(total_pages):
            page = doc[idx]
            text = page.get_text("text")
            if text and text.strip():
                pages_data.append({
                    "page": idx + 1,
                    "text": text.strip()
                })
            else:
                # Try getting blocks if standard get_text is empty
                blocks = page.get_text("blocks")
                block_texts = [b[4] for b in blocks if len(b) > 4 and b[4].strip()]
                if block_texts:
                    pages_data.append({
                        "page": idx + 1,
                        "text": "\n".join(block_texts).strip()
                    })
        doc.close()
    except Exception:
        pages_data = []

    # 2. Fallback: pypdf if fitz encountered any issue
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

    # 3. Fallback: PyPDF2
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

    # Safe fallback if scanned image-only PDF
    if not pages_data:
        total_pages = max(1, total_pages)
        pages_data.append({
            "page": 1,
            "text": "[Note: Scanned or image-based document without embedded text layer.]"
        })

    return pages_data, total_pages

def chunk_document(filename, pages_data, chunk_size=500, chunk_overlap=100):
    """
    Granular chunking across the entire document without limits.
    Creates as many chunks as needed to capture every paragraph, section, and page.
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
    Reads the complete PDF without limits, splits into as many granular chunks
    as possible, and indexes every chunk into ChromaDB Vector Database.
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
        
    # 1. Granular chunking: creates maximum chunks for dense vector search
    chunks = chunk_document(filename, pages_data, chunk_size=500, chunk_overlap=100)
    
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