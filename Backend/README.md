🧠 Study Mentor AI - Backend

This is the backend service for the Study Mentor AI application. It provides a RESTful API built with Flask that handles document processing (PDF/TXT), manages context-aware AI interactions using Groq (Llama 3), and serves as the bridge between the React frontend and the LLM.

🚀 Features

RAG (Retrieval-Augmented Generation): Context-aware responses based on uploaded study materials.

Document Processing: Robust parsing of PDF and TXT files using PyPDF2.

AI Integration: Utilizes the high-performance Groq API with llama-3.3-70b for near-instant inference.

Modular Architecture: Built using Flask Blueprints and the Application Factory pattern for scalability.

CORS Support: Configured for seamless communication with React/Next.js frontends.

🛠️ Tech Stack

Language: Python 3.9+

Framework: Flask

AI Inference: Groq Cloud API

Document Parsing: PyPDF2

Environment Management: python-dotenv

📂 Project Structure

backend/
├── app/
│   ├── __init__.py         # App Factory & Configuration
│   ├── config.py           # Environment configurations
│   ├── routes/             # API Endpoints
│   │   └── api.py
│   └── services/           # Business Logic
│       ├── ai_service.py   # AI & Groq integration
│       └── file_service.py # File parsing logic
├── .env.example            # Template for environment variables
├── requirements.txt        # Python dependencies
├── run.py                  # Entry point
└── README.md


⚡ Getting Started

1. Prerequisites

Python 3.8 or higher installed.

A Groq API Key (Get one at console.groq.com).

2. Installation

Clone the repository:

git clone <your-repo-url>
cd backend


Create a Virtual Environment:

# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate


Install Dependencies:

pip install -r requirements.txt


3. Configuration

Create a .env file in the root directory:

cp .env.example .env  # Or just create a new file named .env


Add your API Key to .env:

GROQ_API_KEY=gsk_your_actual_api_key_here
FLASK_ENV=development


4. Running the Server

Start the Flask development server:

python run.py


You should see:

🚀 Starting Flask Backend...
📡 API configured: True
 * Running on [http://0.0.0.0:5000](http://0.0.0.0:5000)


🔌 API Documentation

1. Health Check

Verifies if the API is running and the API Key is configured.

Endpoint: GET /api/health

Response:

{
  "status": "healthy",
  "api_configured": true,
  "timestamp": "2024-03-20T10:00:00"
}


2. Upload Documents

Uploads study materials to be processed for context.

Endpoint: POST /api/upload

Content-Type: multipart/form-data

Body: files (Array of files)

Response:

{
  "files": [
    { "name": "notes.pdf", "content": "extracted text...", "size": 1024 }
  ],
  "count": 1
}


3. Chat with AI

Sends chat history + document context to the AI.

Endpoint: POST /api/chat

Body:

{
  "messages": [
    { "role": "user", "content": "Explain the concept of RAG." }
  ],
  "uploaded_materials": [
    { "name": "notes.pdf", "content": "extracted text..." }
  ]
}


Response:

{
  "response": "Retrieval-Augmented Generation (RAG) is...",
  "timestamp": "..."
}


🧪 Testing

You can test the API functionality using the built-in test endpoint:

# Browser or Postman
GET http://localhost:5000/api/test


This will send a simple "Hello" to the Groq API to ensure your credentials are working.

📝 License

This project is open-source and available under the MIT License.