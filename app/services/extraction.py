import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Check if fitz (PyMuPDF) is installed
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

# Check if pdfplumber is installed
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

# Check if pytesseract & pdf2image are installed
try:
    import pytesseract
    from pdf2image import convert_from_path
    HAS_OCR = True
except ImportError:
    HAS_OCR = False


class ExtractionService:

    @classmethod
    def extract_document(cls, file_path: str, enable_ocr: bool = True) -> Dict[str, Any]:
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == ".pdf":
            return cls._extract_pdf(file_path, enable_ocr=enable_ocr)
        elif ext in {".txt", ".md"}:
            return cls._extract_text_file(file_path)
        elif ext == ".json":
            return cls._extract_json_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @classmethod
    def _extract_pdf(cls, file_path: str, enable_ocr: bool = True) -> Dict[str, Any]:
        pages_content = []
        sections = []
        tables = []
        
        # 1. Primary Text & Section Extraction using PyMuPDF if available
        if HAS_PYMUPDF:
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            for page_num in range(total_pages):
                page = doc[page_num]
                page_text = page.get_text("text") or ""
                
                # Check for headers/sections using font size / blocks
                blocks = page.get_text("blocks")
                for block in blocks:
                    block_text = block[4].strip()
                    # Heuristic for section titles: short lines starting with numbers or capital title
                    if len(block_text) < 100 and block_text and block_text[0].isupper() and "\n" not in block_text:
                        sections.append({
                            "section_id": f"sec_{len(sections)+1}",
                            "title": block_text,
                            "level": 1,
                            "page_number": page_num + 1,
                            "content": ""
                        })
                
                # Check if OCR fallback is required for scanned page
                used_ocr = False
                if enable_ocr and len(page_text.strip()) < 50 and HAS_OCR:
                    try:
                        pix = page.get_pixmap()
                        img_bytes = pix.tobytes("png")
                        import io
                        from PIL import Image
                        img = Image.open(io.BytesIO(img_bytes))
                        ocr_text = pytesseract.image_to_string(img)
                        if len(ocr_text.strip()) > len(page_text.strip()):
                            page_text = ocr_text
                            used_ocr = True
                    except Exception as err:
                        logger.warning(f"OCR execution skipped/failed on page {page_num+1}: {err}")

                pages_content.append({
                    "page_number": page_num + 1,
                    "text": page_text,
                    "has_ocr": used_ocr
                })
            doc.close()
        
        # 2. Table Extraction using pdfplumber if available
        if HAS_PDFPLUMBER:
            try:
                with pdfplumber.open(file_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        extracted_tables = page.extract_tables()
                        for t_idx, tbl in enumerate(extracted_tables):
                            if tbl and len(tbl) > 1:
                                headers = [str(cell or "").strip() for cell in tbl[0]]
                                rows = [[str(cell or "").strip() for cell in row] for row in tbl[1:]]
                                tables.append({
                                    "table_id": f"tbl_p{i+1}_{t_idx+1}",
                                    "page_number": i + 1,
                                    "headers": headers,
                                    "rows": rows,
                                    "caption": None
                                })
            except Exception as e:
                logger.warning(f"pdfplumber table extraction warning: {e}")

        # Fallback if fitz wasn't available
        if not HAS_PYMUPDF:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages_content.append({
                    "page_number": i + 1,
                    "text": text,
                    "has_ocr": False
                })

        return {
            "total_pages": len(pages_content),
            "pages": pages_content,
            "sections": sections,
            "tables": tables
        }

    @classmethod
    def _extract_text_file(cls, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        lines = text.splitlines()
        sections = []
        for i, line in enumerate(lines):
            line_str = line.strip()
            if line_str.startswith("#"):
                level = len(line_str) - len(line_str.lstrip("#"))
                title = line_str.lstrip("#").strip()
                sections.append({
                    "section_id": f"sec_{len(sections)+1}",
                    "title": title,
                    "level": min(level, 6),
                    "page_number": 1,
                    "content": ""
                })

        return {
            "total_pages": 1,
            "pages": [{"page_number": 1, "text": text, "has_ocr": False}],
            "sections": sections,
            "tables": []
        }

    @classmethod
    def _extract_json_file(cls, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return {
            "total_pages": 1,
            "pages": [{"page_number": 1, "text": text, "has_ocr": False}],
            "sections": [],
            "tables": []
        }
