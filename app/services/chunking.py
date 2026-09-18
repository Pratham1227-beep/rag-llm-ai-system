import uuid
from typing import List, Dict, Any
from app.models.okf_schema import OKFDocument

class DocumentChunker:

    @classmethod
    def chunk_okf_document(
        cls,
        okf_doc: OKFDocument,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> List[Dict[str, Any]]:
        chunks = []
        doc_id = okf_doc.metadata.document_id
        filename = okf_doc.metadata.filename

        # Helper to find section title for page number
        def get_section_for_page(page_num: int) -> str:
            matched_sections = [s for s in okf_doc.sections if s.page_number <= page_num]
            if matched_sections:
                return matched_sections[-1].title
            return "General"

        chunk_counter = 0

        # 1. Chunk Page Content
        for page in okf_doc.page_contents:
            text = page.text.strip()
            if not text:
                continue

            section_title = get_section_for_page(page.page_number)
            
            # Divide page text into overlapping windows
            start = 0
            text_len = len(text)
            
            while start < text_len:
                end = min(start + chunk_size, text_len)
                chunk_str = text[start:end].strip()
                
                if len(chunk_str) > 20:  # Skip tiny noise
                    chunk_counter += 1
                    chunk_id = f"{doc_id}_p{page.page_number}_c{chunk_counter}"
                    
                    chunks.append({
                        "chunk_id": chunk_id,
                        "document_id": doc_id,
                        "filename": filename,
                        "page_number": page.page_number,
                        "section_title": section_title,
                        "chunk_index": chunk_counter,
                        "text": chunk_str,
                        "metadata": {
                            "document_id": doc_id,
                            "filename": filename,
                            "page_number": page.page_number,
                            "section_title": section_title,
                            "chunk_index": chunk_counter,
                            "type": "text"
                        }
                    })

                if end >= text_len:
                    break
                start += (chunk_size - chunk_overlap)

        # 2. Chunk Tables separately with Markdown representations
        for tbl in okf_doc.tables:
            if tbl.headers and tbl.rows:
                table_md_lines = [" | ".join(tbl.headers), " | ".join(["---"] * len(tbl.headers))]
                for row in tbl.rows:
                    table_md_lines.append(" | ".join(row))
                
                table_text = f"Table on Page {tbl.page_number} ({tbl.section_title or 'Data'}):\n" + "\n".join(table_md_lines)
                chunk_counter += 1
                chunk_id = f"{doc_id}_tbl_p{tbl.page_number}_c{chunk_counter}"
                
                chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": doc_id,
                    "filename": filename,
                    "page_number": tbl.page_number,
                    "section_title": tbl.section_title or "Tables",
                    "chunk_index": chunk_counter,
                    "text": table_text,
                    "metadata": {
                        "document_id": doc_id,
                        "filename": filename,
                        "page_number": tbl.page_number,
                        "section_title": tbl.section_title or "Tables",
                        "chunk_index": chunk_counter,
                        "type": "table"
                    }
                })

        return chunks
