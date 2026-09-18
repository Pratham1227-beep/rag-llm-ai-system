import time
from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.services.vectordb import VectorDBService
from app.services.ollama_client import OllamaClient
from app.services.evaluator import GroundingEvaluator
from app.config import settings

router = APIRouter(prefix="/query", tags=["query"])

@router.post("", response_model=QueryResponse)
def execute_query(req: QueryRequest):
    start_time = time.time()

    # 1. Similarity search in ChromaDB
    retrieved_chunks = VectorDBService.similarity_search(
        query=req.query,
        top_k=req.top_k,
        document_ids=req.document_ids
    )

    # 2. LLM response generation via Ollama
    answer, citations = OllamaClient.generate_grounded_response(
        query=req.query,
        retrieved_chunks=retrieved_chunks,
        model_override=req.model
    )

    # 3. Groundedness Evaluation
    groundedness = GroundingEvaluator.evaluate_groundedness(answer, citations)

    processing_time = round(time.time() - start_time, 2)

    return QueryResponse(
        query=req.query,
        answer=answer,
        citations=citations,
        llm_model=req.model or settings.OLLAMA_MODEL,
        retrieval_count=len(retrieved_chunks),
        processing_time_seconds=processing_time,
        groundedness_score=groundedness
    )
