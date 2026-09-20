import json
from pathlib import Path
from typing import Dict, Any, Optional
from app.config import settings
from app.models.okf_schema import (
    OKFDocument, OKFDocumentMetadata, OKFSection, OKFTable, OKFPageContent, OKFKeyValuePair
)

class OKFService:

    @classmethod
    def create_okf_document(
        cls,
        doc_id: str,
        filename: str,
        file_size_bytes: int,
        file_type: str,
        extracted_data: Dict[str, Any]
    ) -> OKFDocument:
        metadata = OKFDocumentMetadata(
            document_id=doc_id,
            filename=filename,
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            total_pages=extracted_data.get("total_pages", 1),
            title=extracted_data.get("pdf_metadata", {}).get("title"),
            author=extracted_data.get("pdf_metadata", {}).get("author"),
            custom_metadata={
                k: v for k, v in extracted_data.get("pdf_metadata", {}).items()
                if k not in ("title", "author")
            }
        )

        sections = [
            OKFSection(**sec) for sec in extracted_data.get("sections", [])
        ]

        tables = [
            OKFTable(**tbl) for tbl in extracted_data.get("tables", [])
        ]

        pages = [
            OKFPageContent(**pg) for pg in extracted_data.get("pages", [])
        ]

        okf_doc = OKFDocument(
            metadata=metadata,
            sections=sections,
            tables=tables,
            page_contents=pages
        )

        cls.save_okf_document(okf_doc)
        return okf_doc

    @classmethod
    def save_okf_document(cls, okf_doc: OKFDocument) -> Path:
        settings.ensure_directories()
        json_path = Path(settings.OKF_STORE_DIR) / f"{okf_doc.metadata.document_id}.json"
        md_path = Path(settings.OKF_STORE_DIR) / f"{okf_doc.metadata.document_id}.md"
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(okf_doc.model_dump_json(indent=2))
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(okf_doc.to_markdown())
        return json_path

    @classmethod
    def load_okf_document(cls, doc_id: str) -> Optional[OKFDocument]:
        file_path = Path(settings.OKF_STORE_DIR) / f"{doc_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return OKFDocument(**data)
