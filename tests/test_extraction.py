import os
import tempfile
from app.services.extraction import ExtractionService

def test_extract_text_file():
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".md", delete=False, encoding="utf-8") as tmp:
        tmp.write("# Executive Summary\nThis is an enterprise RAG system.\n\n## Architecture\nUses OKF format.")
        tmp_path = tmp.name

    try:
        extracted = ExtractionService.extract_document(tmp_path)
        assert extracted["total_pages"] == 1
        assert len(extracted["pages"]) == 1
        assert "Executive Summary" in extracted["pages"][0]["text"]
        assert len(extracted["sections"]) == 2
        assert extracted["sections"][0]["title"] == "Executive Summary"
        assert extracted["sections"][1]["title"] == "Architecture"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
