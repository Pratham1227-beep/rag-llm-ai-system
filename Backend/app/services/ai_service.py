import groq
from flask import current_app
from app.services import vector_service

def get_groq_client():
    api_key = current_app.config.get('GROQ_API_KEY')
    if not api_key:
        raise ValueError("GROQ_API_KEY not found")
    return groq.Groq(api_key=api_key)

def get_available_chat_model(client, preferred=None):
    """Dynamically query Groq's active models list to pick the best supported model."""
    try:
        models_data = client.models.list()
        available_ids = [m.id for m in models_data.data if getattr(m, 'active', True)]
        
        if preferred and preferred in available_ids:
            return preferred
            
        priority = [
            'llama-3.3-70b-versatile',
            'llama-3.1-8b-instant',
            'llama-3.1-70b-versatile',
            'llama-3.2-3b-preview',
            'llama-3.2-1b-preview',
            'gemma2-9b-it',
            'mixtral-8x7b-32768',
            'qwen-qwq-32b',
            'deepseek-r1-distill-llama-70b',
        ]
        for p in priority:
            if p in available_ids:
                return p
                
        # Filter out audio/moderation models
        chat_models = [m for m in available_ids if 'whisper' not in m and 'guard' not in m and 'safeguard' not in m]
        if chat_models:
            return chat_models[0]
        if available_ids:
            return available_ids[0]
    except Exception:
        pass
    # Fall back to the configured preferred model, then a safe known default
    return preferred or 'llama-3.1-8b-instant'

def generate_ai_response(messages, uploaded_materials=None):
    client = get_groq_client()
    
    # 1. Extract the latest user query for Vector DB similarity retrieval
    user_query = ""
    for m in reversed(messages):
        if m.get('role') == 'user':
            user_query = m.get('content', '')
            break

    # 2. Retrieve top semantic chunks from ChromaDB Vector Database
    retrieved_chunks = []
    if user_query:
        try:
            retrieved_chunks = vector_service.search_relevant_chunks(user_query, top_k=6)
        except Exception as e:
            current_app.logger.warning(f"Vector search warning: {e}")

    # 3. Build enterprise RAG system prompt
    system_content = (
        "You are an intelligent, high-precision Enterprise RAG AI Assistant powered by a persistent Vector Database (ChromaDB).\n"
        "Your primary goal is to answer questions accurately and insightfully based on the retrieved document chunks and uploaded context.\n\n"
        "RAG Retrieval & Citation Rules:\n"
        "- Base your answers on the relevant document chunks retrieved from the Vector Database and any provided document context.\n"
        "- When quoting or using information from the documents, ALWAYS cite the source document name and page number (e.g., [Document: filename.pdf, Page X]).\n"
        "- If the retrieved chunks or documents do not contain enough information to answer completely, state clearly what is found and what is missing.\n\n"
        "Language & Tone Rules:\n"
        "- ALWAYS communicate and answer in English unless the user explicitly asks for another language.\n"
        "- Maintain a professional, articulate, and helpful enterprise tone.\n\n"
        "Formatting Guidelines:\n"
        "- Use Markdown formatting effectively: headers (##, ###), bullet points, bold key terms, and clean tables when comparing data.\n"
        "- Keep explanations direct, professional, and well-organized with clear section headings."
    )
    
    # Inject Vector DB Retrieved Chunks
    if retrieved_chunks:
        system_content += "\n\n=== RELEVANT CONTEXT RETRIEVED FROM VECTOR DATABASE (CHROMADB CHUNKS) ===\n"
        for i, chunk in enumerate(retrieved_chunks, 1):
            system_content += (
                f"\n[Vector Chunk {i} | Source: {chunk['source']} | Page: {chunk['page']} | Match Score: {chunk['similarity_score']}]\n"
                f"{chunk['text']}\n"
            )

    # Inject full active session materials if provided
    if uploaded_materials:
        system_content += "\n\n=== UPLOADED DOCUMENT REFERENCE CONTEXT ===\n"
        for material in uploaded_materials:
            doc_name = material.get('name', 'Uploaded Document')
            doc_content = material.get('content', '')
            system_content += f"\n--- Document: {doc_name} ---\n{doc_content}\n"
    
    api_messages = [{"role": "system", "content": system_content}]
    api_messages.extend(messages)
    
    preferred_model = current_app.config.get('GROQ_MODEL')
    selected_model = get_available_chat_model(client, preferred_model)
    
    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=api_messages,
            max_tokens=4096,
            temperature=0.7,
        )
        return {
            "content": response.choices[0].message.content,
            "retrieved_chunks_count": len(retrieved_chunks),
            "sources": [
                {
                    "source": c["source"],
                    "page": c["page"],
                    "similarity": c["similarity_score"]
                }
                for c in retrieved_chunks
            ]
        }
    except Exception as primary_error:
        # If primary fails, query live models and try each active chat model
        try:
            models_data = client.models.list()
            chat_models = [
                m.id for m in models_data.data 
                if getattr(m, 'active', True) 
                and 'whisper' not in m.id 
                and 'guard' not in m.id 
                and 'safeguard' not in m.id 
                and m.id != selected_model
            ]
            for model in chat_models:
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=api_messages,
                        max_tokens=4096,
                        temperature=0.7,
                    )
                    return {
                        "content": response.choices[0].message.content,
                        "retrieved_chunks_count": len(retrieved_chunks),
                        "sources": [
                            {
                                "source": c["source"],
                                "page": c["page"],
                                "similarity": c["similarity_score"]
                            }
                            for c in retrieved_chunks
                        ]
                    }
                except Exception:
                    continue
        except Exception:
            pass
        raise Exception(f"AI API Error: {str(primary_error)}")