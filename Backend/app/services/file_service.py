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

def get_adaptive_chunk_params(total_pages):
    """
    Dynamically selects chunk_size and overlap based on document length.
    Balances retrieval accuracy (small chunks) with indexing speed (large chunks).

    Strategy:
      - Small docs  (1–10 pages)  : 500 chars / 100 overlap  → fine-grained, highest precision
      - Medium docs (11–25 pages) : 800 chars / 130 overlap  → balanced accuracy & speed
      - Large docs  (26–60 pages) : 1200 chars / 180 overlap → speed-optimized, still accurate
      - XL docs     (61+ pages)   : 1600 chars / 240 overlap → maximum throughput, broad coverage
    """
    if total_pages <= 10:
        return 500, 100
    elif total_pages <= 25:
        return 800, 130
    elif total_pages <= 60:
        return 1200, 180
    else:
        return 1600, 240

def chunk_document(filename, pages_data, total_pages):
    """
    Adaptive chunking across the entire document without any page or content limits.
    Chunk size is automatically chosen based on document length for the optimal
    balance of retrieval accuracy and indexing speed.
    Every page is always fully covered — no content is ever skipped.
    """
    chunk_size, chunk_overlap = get_adaptive_chunk_params(total_pages)
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
            
    return chunks, chunk_size

def process_uploaded_file(file):
    """
    Reads the COMPLETE PDF across every page without limits.
    Uses adaptive chunk sizing so every document gets the best
    balance of retrieval accuracy and indexing speed.
    All content from all pages is always covered.
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
        
    # 1. Adaptive chunking — chunk size auto-scales with document size
    chunks, chunk_size_used = chunk_document(filename, pages_data, total_pages)
    
    # 2. Ingest into ChromaDB Vector Database (batched upsert)
    db_result = vector_service.add_chunks_to_vector_db(chunks)
    
    total_in_db = db_result.get("total_chunks_in_db", 0)
    
    return {
        "name": filename,
        "content": full_text,
        "size": len(file_bytes),
        "type": file.content_type,
        "total_pages": total_pages,
        "chunks_created": len(chunks),
        "chunk_size_used": chunk_size_used,
        "vector_db_status": "indexed",
        "total_chunks_in_db": total_in_db
    }