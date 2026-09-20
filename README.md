# 🧠 Enterprise RAG + LLM AI System

**A Modular, Production-Ready Retrieval-Augmented Generation Pipeline**
**with Open Knowledge Format (OKF), ChromaDB Vector Search & Local LLM Inference**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20DB-orange)](https://www.trychroma.com)
[![Ollama](https://img.shields.io/badge/Ollama-LLM%20Runtime-black?logo=ollama)](https://ollama.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture & Pipeline](#-architecture--pipeline)
- [Key Features](#-key-features)
- [Open Knowledge Format (OKF)](#-open-knowledge-format-okf)
- [Repository Structure](#-repository-structure)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Configuration](#-configuration)
- [Deployment](#-deployment)

---

## Overview

This system implements a **full end-to-end RAG pipeline** that converts unstructured documents (PDF, TXT, Markdown, JSON) into a structured intermediate representation called **Open Knowledge Format (OKF)**, chunks them with boundary-aware tokenization, indexes them into a **ChromaDB** vector store using `sentence-transformers/all-MiniLM-L6-v2` embeddings, and generates grounded, citation-backed responses via a locally hosted **Ollama** LLM (e.g. `llama3.2`).

---

## 🏗 Architecture & Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER / WEB UI (localhost:8000)                    │
│                 Upload PDF  ─→  Ask Questions  ─→  Get Answers          │
└────────────┬──────────────────────────────────────────────┬──────────────┘
             │  POST /documents/upload                     │  POST /query
             ▼                                             ▼
┌─────────────────────┐                        ┌──────────────────────────┐
│  1. INGESTION       │                        │  5. QUERY PIPELINE       │
│  ─────────────────  │                        │  ────────────────────    │
│  • File validation  │                        │  • Embed user query      │
│  • UUID assignment  │                        │  • Cosine similarity     │
│  • Save to disk     │                        │    search in ChromaDB    │
│  • Registry update  │                        │  • Top-K chunk retrieval │
└────────┬────────────┘                        └────────────┬─────────────┘
         │  POST /documents/process                         │
         ▼                                                  ▼
┌─────────────────────┐                        ┌──────────────────────────┐
│  2. EXTRACTION      │                        │  6. LLM GENERATION       │
│  ─────────────────  │                        │  ────────────────────    │
│  • PyMuPDF text     │                        │  • Grounded system       │
│  • pdfplumber       │                        │    prompt construction   │
│    table extraction │                        │  • Ollama API call       │
│  • PyTesseract OCR  │                        │    (llama3.2 / mistral)  │
│    fallback for     │                        │  • Inline source         │
│    scanned pages    │                        │    citations [Source N]  │
│  • Section header   │                        │  • Fallback response     │
│    detection        │                        │    if Ollama is offline   │
└────────┬────────────┘                        └────────────┬─────────────┘
         │                                                  │
         ▼                                                  ▼
┌─────────────────────┐                        ┌──────────────────────────┐
│  3. OKF CONVERSION  │                        │  7. GROUNDING EVALUATION │
│  ─────────────────  │                        │  ────────────────────    │
│  • Structured JSON  │                        │  • Token overlap scoring │
│  • Markdown (.md)   │                        │  • Answer vs. citations  │
│  • Metadata, pages, │                        │  • Groundedness score    │
│    sections, tables │                        │    (0.0 → 1.0)          │
│  • Saved to         │                        │  • Stop-word filtering   │
│    data/okf_store/  │                        └──────────────────────────┘
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  4. CHUNKING &      │
│     INDEXING        │
│  ─────────────────  │
│  • Boundary-aware   │
│    sentence splits  │
│  • Configurable     │
│    chunk_size (500) │
│    & overlap (50)   │
│  • Table→Markdown   │
│    chunk conversion │
│  • MiniLM-L6-v2     │
│    embedding (384d) │
│  • ChromaDB HNSW    │
│    cosine upsert    │
└─────────────────────┘
```

### Pipeline Flow Summary

| Stage | Service | Input | Output |
|-------|---------|-------|--------|
| **1. Ingestion** | `IngestionService` | Uploaded file (PDF/TXT/MD/JSON) | Saved file + registry entry |
| **2. Extraction** | `ExtractionService` | Raw file on disk | Pages, sections, tables (dict) |
| **3. OKF Conversion** | `OKFService` | Extracted data dict | `.json` + `.md` in `data/okf_store/` |
| **4. Chunking** | `DocumentChunker` | OKF document model | Boundary-aware text chunks |
| **5. Embedding & Indexing** | `EmbeddingService` + `VectorDBService` | Text chunks | 384-dim vectors in ChromaDB |
| **6. Query & Retrieval** | `VectorDBService` | User query string | Top-K relevant chunks |
| **7. LLM Generation** | `OllamaClient` | Query + retrieved context | Grounded answer + citations |
| **8. Evaluation** | `GroundingEvaluator` | Answer + citations | Groundedness score (0.0–1.0) |

---

## 🌟 Key Features

| Feature | Description |
|---------|-------------|
| **Open Knowledge Format (OKF)** | Standardized intermediate representation separating metadata, section hierarchies, tables, and page-level provenance into both JSON and Markdown |
| **Multi-Format Ingestion** | PDF, TXT, Markdown, and JSON documents with automatic format detection |
| **Advanced PDF Extraction** | Primary extraction via **PyMuPDF** with **pdfplumber** table extraction and **PyTesseract** OCR fallback for scanned/image-heavy pages |
| **Boundary-Aware Chunking** | Sentence-boundary snapping prevents mid-word/mid-sentence splits; configurable `chunk_size` and `chunk_overlap` |
| **Semantic Vector Search** | ChromaDB with HNSW cosine index powered by `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional embeddings) |
| **Local LLM Integration** | Ollama API with `llama3.2` (default) or `mistral`; strict grounding prompts enforce citation-backed answers |
| **Groundedness Scoring** | Token-overlap evaluation between generated answer and source citations produces a 0.0–1.0 confidence score |
| **Graceful Degradation** | Falls back to context-based summary when Ollama is offline; mock embeddings when GPU/model unavailable |
| **Web UI** | Built-in single-page HTML interface served at `localhost:8000` for upload, processing, and querying |

---

## 📦 Open Knowledge Format (OKF)

OKF is the **structured intermediate representation** at the heart of this pipeline. Every ingested document is converted into an OKF record stored in **two formats**:

### Storage Location

```
data/okf_store/
├── <document_id>.json      ← Machine-readable (Pydantic model dump)
├── <document_id>.md        ← Human-readable (Markdown with YAML frontmatter)
└── ...
```

### OKF Schema Structure

```
OKFDocument
├── metadata                    # OKFDocumentMetadata
│   ├── document_id             # UUID
│   ├── filename                # Original filename
│   ├── file_type               # .pdf, .txt, .md, .json
│   ├── file_size_bytes         # Size in bytes
│   ├── total_pages             # Page count
│   ├── upload_timestamp        # ISO 8601 UTC timestamp
│   ├── title / author          # Extracted metadata (optional)
│   └── custom_metadata         # Arbitrary key-value pairs
├── sections[]                  # OKFSection
│   ├── section_id / title      # Unique ID + heading text
│   ├── level                   # Heading depth (1=H1, 2=H2, ...)
│   ├── page_number             # Starting page
│   ├── parent_id               # Hierarchical parent (optional)
│   └── content                 # Section body text
├── tables[]                    # OKFTable
│   ├── table_id / page_number  # Unique ID + source page
│   ├── headers[]               # Column header names
│   ├── rows[][]                # Cell values
│   └── caption                 # Table description (optional)
├── key_value_pairs[]           # OKFKeyValuePair (key, value, page)
├── page_contents[]             # OKFPageContent
│   ├── page_number / text      # Full page text
│   └── has_ocr                 # True if OCR was used
└── okf_version: "1.0"
```

### Example OKF Markdown Output

```markdown
---
document_id: "test_doc_123"
filename: "report.pdf"
file_type: ".pdf"
file_size_bytes: 10240
total_pages: 2
upload_timestamp: "2026-09-18T06:49:29.536104+00:00"
okf_version: "1.0"
---

# report.pdf

## Introduction *(Page 1)*

Page 1 intro
```

---

## 📁 Repository Structure

```
rag-llm-ai-system/
├── .env                        # Environment configuration
├── .env.example                # Template for environment variables
├── .gitignore
├── README.md
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Project metadata
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point + CORS + routing
│   ├── config.py               # Pydantic Settings (loaded from .env)
│   │
│   ├── api/                    # API Route Handlers
│   │   ├── routes_documents.py # Upload, process, list, get OKF
│   │   ├── routes_query.py     # RAG query endpoint
│   │   └── routes_health.py    # Health check + status
│   │
│   ├── models/                 # Pydantic Data Models
│   │   ├── schemas.py          # Request/Response schemas
│   │   └── okf_schema.py       # OKF document model + to_markdown()
│   │
│   ├── services/               # Core Business Logic
│   │   ├── ingestion.py        # File upload + registry management
│   │   ├── extraction.py       # PDF/TXT/MD/JSON content extraction
│   │   ├── chunking.py         # Boundary-aware document chunking
│   │   ├── okf.py              # OKF creation, save (JSON+MD), load
│   │   ├── embeddings.py       # SentenceTransformer embedding service
│   │   ├── vectordb.py         # ChromaDB vector store operations
│   │   ├── ollama_client.py    # Ollama LLM API client
│   │   └── evaluator.py        # Groundedness scoring
│   │
│   └── static/
│       └── index.html          # Built-in Web UI
│
├── data/                       # Runtime Data (gitignored)
│   ├── uploads/                # Raw uploaded documents
│   ├── okf_store/              # OKF representations (.json + .md)
│   └── vector_db/              # ChromaDB persistent storage
│
└── tests/                      # Test Suite
    ├── test_api.py             # API endpoint integration tests
    ├── test_ingestion.py       # File ingestion unit tests
    ├── test_extraction.py      # PDF/text extraction tests
    ├── test_okf.py             # OKF creation & persistence tests
    └── test_retrieval.py       # Vector search retrieval tests
```

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.10+ | Runtime |
| Ollama | 0.34+ | Local LLM server |
| Tesseract OCR | (optional) | Scanned PDF fallback |

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/rag-llm-ai-system.git
cd rag-llm-ai-system

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env to set your Ollama model, port, etc.
```

### 3. Start Ollama

```bash
# Pull the default model
ollama pull llama3.2

# Start the Ollama server (if not already running)
ollama serve
```

### 4. Launch the Server

```bash
# Option A: via Python module
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Option B: run main.py directly
python app/main.py
```

### 5. Access the Application

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Web UI (upload, process, query) |
| http://localhost:8000/docs | Swagger API Documentation |
| http://localhost:8000/redoc | ReDoc API Documentation |

---

## 🔌 API Reference

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health: ChromaDB index count, Ollama connectivity, model availability |

### Document Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/documents/upload` | Upload a document (PDF, TXT, MD, JSON). Returns `document_id` |
| `POST` | `/documents/process` | Run the full pipeline: Extract → OKF → Chunk → Index |
| `GET` | `/documents` | List all documents with status, page count, chunk count |
| `GET` | `/documents/{id}` | Retrieve the full OKF JSON representation |

### RAG Query

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/query` | Execute a grounded RAG query with LLM response + citations + groundedness score |

#### Query Request Body

```json
{
  "query": "What are the key findings in the report?",
  "top_k": 4,
  "document_ids": ["<optional-filter>"],
  "model": "llama3.2"
}
```

#### Query Response

```json
{
  "query": "What are the key findings?",
  "answer": "According to the report [Source 1, Page 3]...",
  "citations": [
    {
      "document_id": "uuid-here",
      "filename": "report.pdf",
      "page_number": 3,
      "section_title": "Findings",
      "snippet": "The analysis reveals...",
      "relevance_score": 0.9234
    }
  ],
  "llm_model": "llama3.2",
  "retrieval_count": 4,
  "processing_time_seconds": 2.31,
  "groundedness_score": 0.87
}
```

---

## 🧪 Testing

Run the full test suite:

```bash
pytest -v
```

| Test File | Coverage |
|-----------|----------|
| `test_ingestion.py` | File upload, validation, registry persistence |
| `test_extraction.py` | PDF/TXT/MD/JSON content extraction |
| `test_okf.py` | OKF document creation, JSON+MD persistence, reload |
| `test_retrieval.py` | ChromaDB indexing and similarity search |
| `test_api.py` | FastAPI endpoint integration tests |

---

## ⚙️ Configuration

All settings are loaded from `.env` via **Pydantic Settings**:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `Enterprise RAG + LLM AI System` | Application display name |
| `DEBUG` | `true` | Enable debug mode & auto-reload |
| `PORT` | `8000` | Server port |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3.2` | Default LLM model |
| `OLLAMA_TIMEOUT_SECONDS` | `60.0` | LLM request timeout |
| `VECTOR_DB_DIR` | `./data/vector_db` | ChromaDB persistence path |
| `EMBEDDING_MODEL_NAME` | `all-MiniLM-L6-v2` | SentenceTransformer model |
| `TOP_K_RETRIEVAL` | `4` | Default retrieval count |
| `UPLOAD_DIR` | `./data/uploads` | Uploaded file storage |
| `OKF_STORE_DIR` | `./data/okf_store` | OKF document storage (JSON + MD) |
| `MAX_UPLOAD_SIZE_MB` | `25` | Maximum upload file size |

---

## 🌐 Deployment

### Linux / Bluehost / cPanel

```bash
# 1. Upload repository files to ~/rag-llm-ai-system
# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Install & start Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
ollama serve &

# 4. Run with systemd or supervisor
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Windows Server

```powershell
# 1. Install Ollama from https://ollama.com/download
# 2. Pull model
ollama pull llama3.2

# 3. Start server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---


**Built by [Pratham Khatri](https://github.com/prathamkhatri)** · AI & ML Engineer


