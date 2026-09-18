import os
import uuid
import json
import shutil
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import UploadFile, HTTPException
from app.config import settings

STATUS_FILE = Path(settings.UPLOAD_DIR) / "document_registry.json"

def _load_registry() -> Dict[str, Dict[str, Any]]:
    if STATUS_FILE.exists():
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_registry(registry: Dict[str, Dict[str, Any]]):
    settings.ensure_directories()
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

class IngestionService:
    ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".json"}

    @classmethod
    def save_uploaded_file(cls, file: UploadFile) -> Dict[str, Any]:
        settings.ensure_directories()
        
        filename = file.filename or "unnamed_file"
        file_ext = Path(filename).suffix.lower()

        if file_ext not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{file_ext}'. Allowed formats: {', '.join(cls.ALLOWED_EXTENSIONS)}"
            )

        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        dest_filename = f"{doc_id}_{filename}"
        dest_path = Path(settings.UPLOAD_DIR) / dest_filename

        # Save file to upload directory
        try:
            with open(dest_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

        file_size = dest_path.stat().st_size
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            dest_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

        record = {
            "document_id": doc_id,
            "filename": filename,
            "stored_filename": dest_filename,
            "file_path": str(dest_path),
            "file_size_bytes": file_size,
            "file_type": file_ext,
            "upload_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "uploaded",
            "indexed_chunks": 0
        }

        registry = _load_registry()
        registry[doc_id] = record
        _save_registry(registry)

        return record

    @classmethod
    def get_document(cls, doc_id: str) -> Optional[Dict[str, Any]]:
        registry = _load_registry()
        return registry.get(doc_id)

    @classmethod
    def list_documents(cls) -> List[Dict[str, Any]]:
        registry = _load_registry()
        return list(registry.values())

    @classmethod
    def update_status(cls, doc_id: str, status: str, extra_meta: Optional[Dict[str, Any]] = None):
        registry = _load_registry()
        if doc_id in registry:
            registry[doc_id]["status"] = status
            if extra_meta:
                registry[doc_id].update(extra_meta)
            _save_registry(registry)
