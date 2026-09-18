import logging
import httpx
from typing import List, Dict, Any, Tuple
from app.config import settings
from app.models.schemas import SourceCitation

logger = logging.getLogger(__name__)

class OllamaClient:

    @classmethod
    def check_health(cls) -> Tuple[bool, str]:
        """Checks connection to Ollama service and checks model availability."""
        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags"
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(url)
                if res.status_code == 200:
                    models = [m.get("name") for m in res.json().get("models", [])]
                    model_name = settings.OLLAMA_MODEL
                    matched = any(m.startswith(model_name) for m in models)
                    status = f"connected (models available: {', '.join(models) if models else 'none'})"
                    return True, status
                return False, f"Ollama returned HTTP {res.status_code}"
        except Exception as e:
            return False, f"Ollama connection unavailable at {settings.OLLAMA_BASE_URL} ({str(e)})"

    @classmethod
    def generate_grounded_response(
        cls,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        model_override: str = None
    ) -> Tuple[str, List[SourceCitation]]:
        model = model_override or settings.OLLAMA_MODEL
        citations = []

        # Construct Citations from retrieved chunks
        context_str_parts = []
        for idx, chunk in enumerate(retrieved_chunks, 1):
            citation = SourceCitation(
                document_id=chunk["document_id"],
                filename=chunk["filename"],
                page_number=chunk["page_number"],
                section_title=chunk.get("section_title"),
                snippet=chunk["snippet"][:200] + "..." if len(chunk["snippet"]) > 200 else chunk["snippet"],
                relevance_score=chunk["relevance_score"]
            )
            citations.append(citation)

            context_str_parts.append(
                f"--- [Source {idx}]: {chunk['filename']} (Page {chunk['page_number']}, Section: '{chunk.get('section_title', 'General')}') ---\n"
                f"{chunk['snippet']}"
            )

        context_text = "\n\n".join(context_str_parts)

        # System Prompt construction enforcing grounding
        system_prompt = (
            "You are an enterprise AI document assistant. Answer the user's question based strictly on the provided context.\n"
            "If the context does not contain enough information to answer, state clearly that the document does not mention it.\n"
            "Include inline references to the sources (e.g. [Source 1, Page 2]) when asserting facts.\n\n"
            f"Context:\n{context_text}"
        )

        user_prompt = f"Question: {query}"

        # Call Ollama API
        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"
        payload = {
            "model": model,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }

        try:
            with httpx.Client(timeout=settings.OLLAMA_TIMEOUT_SECONDS) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    answer = res.json().get("response", "").strip()
                    return answer, citations
                else:
                    logger.warning(f"Ollama returned HTTP {res.status_code}. Using fallback summary generator.")
        except Exception as e:
            logger.warning(f"Ollama API request failed ({e}). Generating fallback response from retrieved context.")

        # Fallback response generator if Ollama is not active locally
        if retrieved_chunks:
            fallback_answer = (
                f"Based on the retrieved context from '{retrieved_chunks[0]['filename']}':\n\n"
                f"{retrieved_chunks[0]['snippet']}\n\n"
                f"*(Note: Generated directly from context as Ollama LLM endpoint at {settings.OLLAMA_BASE_URL} is currently offline)*"
            )
        else:
            fallback_answer = "No relevant context found in documents to answer your query."

        return fallback_answer, citations
