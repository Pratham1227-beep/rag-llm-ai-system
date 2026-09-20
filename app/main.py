from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes_documents import router as documents_router
from app.api.routes_query import router as query_router
from app.api.routes_health import router as health_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Modular Enterprise RAG + LLM AI System with Open Knowledge Format (OKF) & ChromaDB",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health_router)
app.include_router(documents_router)
app.include_router(query_router)

from fastapi.responses import HTMLResponse
from pathlib import Path

@app.get("/", response_class=HTMLResponse)
def root():
    static_file = Path(__file__).parent / "static" / "index.html"
    if static_file.exists():
        return HTMLResponse(content=static_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Enterprise RAG System Running</h1><p><a href='/docs'>Swagger API Docs</a></p>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
