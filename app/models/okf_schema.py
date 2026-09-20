import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class OKFDocumentMetadata(BaseModel):
    document_id: str = Field(..., description="Unique identifier for the document")
    filename: str = Field(..., description="Original name of the uploaded file")
    file_type: str = Field(..., description="MIME type or extension of the file")
    upload_timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
        description="Timestamp of ingestion"
    )
    file_size_bytes: int = Field(0, description="Size of file in bytes")
    title: Optional[str] = Field(None, description="Extracted document title")
    author: Optional[str] = Field(None, description="Document author if available")
    total_pages: int = Field(0, description="Total number of pages in the document")
    language: str = Field("en", description="Detected or primary language")
    custom_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional key-value metadata")


class OKFSection(BaseModel):
    section_id: str = Field(..., description="Unique identifier for section")
    title: str = Field(..., description="Section header or title")
    level: int = Field(1, description="Heading level (1=H1, 2=H2, etc.)")
    page_number: int = Field(1, description="Starting page number of the section")
    parent_id: Optional[str] = Field(None, description="Parent section ID for hierarchy")
    content: str = Field("", description="Text content contained within section")


class OKFTable(BaseModel):
    table_id: str = Field(..., description="Unique table identifier")
    page_number: int = Field(1, description="Page number where table appears")
    section_title: Optional[str] = Field(None, description="Associated section title")
    headers: List[str] = Field(default_factory=list, description="Table column header names")
    rows: List[List[str]] = Field(default_factory=list, description="Table row contents")
    caption: Optional[str] = Field(None, description="Table caption or description")


class OKFKeyValuePair(BaseModel):
    key: str
    value: str
    page_number: int = 1


class OKFPageContent(BaseModel):
    page_number: int
    text: str
    has_ocr: bool = False


class OKFDocument(BaseModel):
    metadata: OKFDocumentMetadata
    sections: List[OKFSection] = Field(default_factory=list)
    tables: List[OKFTable] = Field(default_factory=list)
    key_value_pairs: List[OKFKeyValuePair] = Field(default_factory=list)
    page_contents: List[OKFPageContent] = Field(default_factory=list)
    okf_version: str = Field("1.0", description="Open Knowledge Format spec version")

    def get_full_text(self) -> str:
        """Returns aggregated text across all pages."""
        return "\n\n".join([f"--- Page {p.page_number} ---\n{p.text}" for p in self.page_contents])

    def to_markdown(self) -> str:
        """Serializes the OKF Document into standard Open Knowledge Format Markdown with frontmatter."""
        meta = self.metadata
        md_lines = [
            "---",
            f"document_id: \"{meta.document_id}\"",
            f"filename: \"{meta.filename}\"",
            f"file_type: \"{meta.file_type}\"",
            f"file_size_bytes: {meta.file_size_bytes}",
            f"total_pages: {meta.total_pages}",
            f"upload_timestamp: \"{meta.upload_timestamp}\"",
            f"okf_version: \"{self.okf_version}\"",
            "---",
            "",
            f"# {meta.title or meta.filename}",
            ""
        ]

        if self.sections:
            for sec in self.sections:
                heading = "#" * min(sec.level + 1, 6)
                md_lines.append(f"{heading} {sec.title} *(Page {sec.page_number})*")
                if sec.content:
                    md_lines.append("")
                    md_lines.append(sec.content)
                md_lines.append("")

        if self.tables:
            md_lines.append("## Structured Tables")
            md_lines.append("")
            for tbl in self.tables:
                caption = f" - {tbl.caption}" if tbl.caption else ""
                md_lines.append(f"### Table: `{tbl.table_id}` *(Page {tbl.page_number})*{caption}")
                md_lines.append("")
                if tbl.headers:
                    md_lines.append("| " + " | ".join(tbl.headers) + " |")
                    md_lines.append("| " + " | ".join(["---"] * len(tbl.headers)) + " |")
                    for row in tbl.rows:
                        # Clean cell values
                        cleaned_row = [str(c).replace("\n", " ") for c in row]
                        md_lines.append("| " + " | ".join(cleaned_row) + " |")
                    md_lines.append("")

        if not self.sections and self.page_contents:
            for p in self.page_contents:
                ocr_badge = " *(OCR Extracted)*" if p.has_ocr else ""
                md_lines.append(f"## Page {p.page_number}{ocr_badge}")
                md_lines.append("")
                md_lines.append(p.text)
                md_lines.append("")

        return "\n".join(md_lines)
