import PyPDF2
from io import BytesIO

def extract_text_from_pdf(pdf_bytes):
    """Extract text from PDF bytes"""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")

def process_uploaded_file(file):
    """Route file to correct extractor based on extension"""
    filename = file.filename
    file_bytes = file.read()
    
    if filename.lower().endswith('.pdf'):
        content = extract_text_from_pdf(file_bytes)
    elif filename.lower().endswith('.txt'):
        content = file_bytes.decode('utf-8')
    else:
        raise ValueError(f"Unsupported file type: {filename}")
        
    return {
        "name": filename,
        "content": content,
        "size": len(file_bytes),
        "type": file.content_type
    }