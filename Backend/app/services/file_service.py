import PyPDF2
from io import BytesIO

def extract_text_from_pdf(pdf_bytes):
    """Extract full text from PDF bytes across all pages without any limit"""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes), strict=False)
        total_pages = len(pdf_reader.pages)
        text_parts = []
        for idx, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_parts.append(f"[Page {idx + 1} of {total_pages}]\n{page_text.strip()}")
            except Exception:
                continue
        
        if not text_parts:
            return "[PDF document was uploaded, but no extractable text could be found. It may consist of scanned images.]"
            
        return "\n\n".join(text_parts)
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

def process_uploaded_file(file):
    """Route file to correct extractor based on extension"""
    filename = file.filename
    file_bytes = file.read()
    
    if filename.lower().endswith('.pdf'):
        content = extract_text_from_pdf(file_bytes)
    elif filename.lower().endswith('.txt'):
        content = file_bytes.decode('utf-8', errors='ignore')
    else:
        raise ValueError(f"Unsupported file type: {filename}")
        
    return {
        "name": filename,
        "content": content,
        "size": len(file_bytes),
        "type": file.content_type
    }