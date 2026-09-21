import groq
from flask import current_app

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
            'llama-3.1-70b-versatile',
            'llama-3.1-8b-instant',
            'llama-3.2-11b-vision-preview',
            'llama-3.2-3b-preview',
            'llama-3.2-1b-preview',
            'qwen-qwq-32b',
            'deepseek-r1-distill-llama-70b',
            'mixtral-8x7b-32768',
            'gemma2-9b-it'
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
    return preferred or 'llama-3.1-8b-instant'

def generate_ai_response(messages, uploaded_materials=None):
    client = get_groq_client()
    
    system_content = (
        "You are an intelligent, high-precision Enterprise RAG AI Assistant.\n"
        "Your goal is to provide clear, structured, and insightful answers.\n\n"
        "Language & Tone Rules:\n"
        "- ALWAYS communicate and answer in English unless the user explicitly asks you to speak in another language.\n"
        "- Maintain a professional, articulate, and helpful enterprise tone.\n\n"
        "Formatting Guidelines:\n"
        "- Use Markdown formatting effectively: headers (##, ###), bullet points, bold key terms, and clean tables when comparing data.\n"
        "- When providing multi-attribute comparisons, present them in clean Markdown tables.\n"
        "- When citing or quoting uploaded documents, clearly mention the source document name.\n"
        "- Keep explanations direct, professional, and well-organized with clear section headings."
    )
    
    if uploaded_materials:
        system_content += "\n\n=== CONTEXT FROM UPLOADED DOCUMENTS ===\n"
        for material in uploaded_materials:
            system_content += f"\n--- Document: {material['name']} ---\n{material['content'][:4000]}\n"
    
    api_messages = [{"role": "system", "content": system_content}]
    api_messages.extend(messages)
    
    preferred_model = current_app.config.get('GROQ_MODEL')
    selected_model = get_available_chat_model(client, preferred_model)
    
    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=api_messages,
            max_tokens=1000,
            temperature=0.7,
        )
        return response.choices[0].message.content
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
                        max_tokens=1000,
                        temperature=0.7,
                    )
                    return response.choices[0].message.content
                except Exception:
                    continue
        except Exception:
            pass
        raise Exception(f"AI API Error: {str(primary_error)}")