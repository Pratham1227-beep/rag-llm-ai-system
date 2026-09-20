import re
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

        def get_section_for_page(page_num: int) -> str:
            matched_sections = [s for s in okf_doc.sections if s.page_number <= page_num]
            if matched_sections:
                return matched_sections[-1].title
            return "General"

        chunk_counter = 0

        # 1. Chunk Page Content with boundary-aware tokenization
        for page in okf_doc.page_contents:
            text = page.text.strip()
            if not text:
                continue

            section_title = get_section_for_page(page.page_number)
            text_len = len(text)
            start = 0

            while start < text_len:
                target_end = min(start + chunk_size, text_len)

                # Snap target_end to natural sentence or word boundary to prevent truncated tokens
                if target_end < text_len:
                    # Look for sentence boundary (. ! ? \n) within 80 chars before target_end
                    punct_pos = max(
                        text.rfind('. ', start, target_end),
                        text.rfind('?\n', start, target_end),
                        text.rfind('!\n', start, target_end),
                        text.rfind('\n\n', start, target_end)
                    )
                    if punct_pos != -1 and punct_pos > start + (chunk_size // 2):
                        target_end = punct_pos + 1
                    else:
                        # Otherwise snap to last space boundary
                        space_pos = text.rfind(' ', start, target_end)
                        if space_pos != -1 and space_pos > start + (chunk_size // 2):
                            target_end = space_pos

                chunk_str = text[start:target_end].strip()

                if len(chunk_str) > 15:
                    chunk_counter += 1
                    chunk_id = f"{doc_id}_p{page.page_number}_c{chunk_counter}"
                    words = re.findall(r'\w+', chunk_str)
                    estimated_tokens = int(len(words) * 1.3)

                    chunks.append({
                        "chunk_id": chunk_id,
                        "document_id": doc_id,
                        "filename": filename,
                        "page_number": page.page_number,
                        "section_title": section_title,
                        "chunk_index": chunk_counter,
                        "text": chunk_str,
                        "token_count_est": estimated_tokens,
                        "metadata": {
                            "document_id": doc_id,
                            "filename": filename,
                            "page_number": page.page_number,
                            "section_title": section_title,
                            "chunk_index": chunk_counter,
                            "token_count_est": estimated_tokens,
                            "type": "text"
                        }
                    })

                if target_end >= text_len:
                    break

                # Advance with overlap
                next_start = target_end - chunk_overlap
                if next_start <= start:
                    next_start = start + 1
                start = next_start

        # 2. Chunk Tables separately into structured Markdown representations
        for tbl in okf_doc.tables:
            if tbl.headers and tbl.rows:
                table_md_lines = [" | ".join(tbl.headers), " | ".join(["---"] * len(tbl.headers))]
                for row in tbl.rows:
                    table_md_lines.append(" | ".join(row))

                table_text = f"Table on Page {tbl.page_number} ({tbl.section_title or 'Data'}):\n" + "\n".join(table_md_lines)
                chunk_counter += 1
                chunk_id = f"{doc_id}_tbl_p{tbl.page_number}_c{chunk_counter}"
                words = re.findall(r'\w+', table_text)
                estimated_tokens = int(len(words) * 1.3)

                chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": doc_id,
                    "filename": filename,
                    "page_number": tbl.page_number,
                    "section_title": tbl.section_title or "Tables",
                    "chunk_index": chunk_counter,
                    "text": table_text,
                    "token_count_est": estimated_tokens,
                    "metadata": {
                        "document_id": doc_id,
                        "filename": filename,
                        "page_number": tbl.page_number,
                        "section_title": tbl.section_title or "Tables",
                        "chunk_index": chunk_counter,
                        "token_count_est": estimated_tokens,
                        "type": "table"
                    }
                })

        return chunks
