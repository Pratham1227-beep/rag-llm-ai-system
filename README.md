# Enterprise RAG + LLM AI System

A modular, production-ready Retrieval-Augmented Generation (RAG) system with **Open Knowledge Format (OKF)** representation, vector search (**ChromaDB**), and local LLM integration (**Ollama**).

---

## 🌟 Key Features

1. **Open Knowledge Format (OKF)**: Standardized document intermediate representation separating metadata, section hierarchies, tables, and page-level provenance.
2. **Multi-Format Ingestion**: Supports PDF, TXT, Markdown, and JSON documents.
3. **Advanced Extraction & OCR Fallback**: Extracted via PyMuPDF and `pdfplumber` with automatic PyTesseract OCR fallback for scanned pages.
4. **Vector Search**: ChromaDB with `sentence-transformers/all-MiniLM-L6-v2` embeddings.
5. **LLM Integration**: Ollama API (`llama3.2` / `mistral`) with strict grounding prompts and source citations.
6. **Portable Architecture**: Designed to run seamlessly across Windows Server and Linux (Bluehost / cPanel) environments.

---

## 📁 Repository Structure

```
rag-llm-ai-system/
├── .env
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── pyproject.toml
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── routes_documents.py
│   │   ├── routes_query.py
│   │   └── routes_health.py
│   ├── models/
│   │   ├── schemas.py
│   │   └── okf_schema.py
│   └── services/
│       ├── ingestion.py
│       ├── extraction.py
│       ├── chunking.py
│       ├── okf.py
│       ├── embeddings.py
│       ├── vectordb.py
│       ├── ollama_client.py
│       └── evaluator.py
├── data/
│   ├── uploads/
│   ├── okf_store/
│   └── vector_db/
└── tests/
    ├── test_ingestion.py
    ├── test_extraction.py
    ├── test_okf.py
    ├── test_retrieval.py
    └── test_api.py
```

---

## 🚀 Quick Start & Installation

### 1. Requirements & Prerequisites
- Python 3.10+
- (Optional) [Ollama](https://ollama.com/) running locally with model `llama3.2`:
  ```bash
  ollama pull llama3.2
  ```

### 2. Virtual Environment & Dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Running the Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Access API Documentation at: `http://localhost:8000/docs`

---

## 🛠️ API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health, ChromaDB index status, Ollama status |
| `POST` | `/documents/upload` | Upload document file (PDF, TXT, MD, JSON) |
| `POST` | `/documents/process` | Extract content, create OKF, chunk & index into Vector DB |
| `GET` | `/documents` | List uploaded documents and status |
| `GET` | `/documents/{id}` | Fetch document OKF JSON representation |
| `POST` | `/query` | Execute RAG search, generate LLM response with citations |

---

## 🧪 Running Tests

Run unit and integration tests using pytest:
```bash
pytest -v
```

---

## 🌐 Bluehost & Linux Deployment Guide

1. Upload repository files to `~/rag-llm-ai-system`.
2. Create Python virtual environment via cPanel or SSH:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Setup systemd service or Passenger WSGI entrypoint (`passenger_wsgi.py`).
