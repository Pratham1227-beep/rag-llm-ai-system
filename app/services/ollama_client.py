import logging
import httpx
from typing import List, Dict, Any, Tuple
from app.config import settings


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
    ) -> str:
        model = model_override or settings.OLLAMA_MODEL

        # Construct Context from retrieved chunks
        context_str_parts = []
        for idx, chunk in enumerate(retrieved_chunks, 1):
            context_str_parts.append(
                f"--- [Source {idx}]: {chunk['filename']} (Page {chunk['page_number']}, Section: '{chunk.get('section_title', 'General')}') ---\n"
                f"{chunk['snippet']}"
            )

        context_text = "\n\n".join(context_str_parts)

        # System Prompt construction allowing RAG context priority + general knowledge fallback
        system_prompt = (
            "You are an AI document assistant. Answer the user's question accurately.\n"
            "Use the provided context if it contains relevant information for the question.\n"
            "If the question is out of context or not mentioned in the documents, answer it directly using your general knowledge.\n"
            "Do NOT mention any source names, document titles, or page numbers in your response.\n"
            "CRITICAL: Answer ONLY the specific question asked. Do NOT include any conversational preamble, filler, or extra introductory phrases.\n\n"
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
                    return answer
                else:
                    logger.warning(f"Ollama returned HTTP {res.status_code}. Using fallback summary generator.")
        except Exception as e:
            logger.warning(f"Ollama API request failed ({e}). Generating fallback response from retrieved context.")

        # Fallback response generator if Ollama is not active locally
        if retrieved_chunks:
            fallback_answer = (
                f"Based on the retrieved context:\n\n"
                f"{retrieved_chunks[0]['snippet']}\n\n"
                f"*(Note: Generated directly from context as Ollama LLM endpoint at {settings.OLLAMA_BASE_URL} is currently offline)*"
            )
        else:
            fallback_answer = "The document does not mention this information."

        return fallback_answer
