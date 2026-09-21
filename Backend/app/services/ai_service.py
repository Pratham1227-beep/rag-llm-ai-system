import groq
from flask import current_app

def get_groq_client():
    api_key = current_app.config['GROQ_API_KEY']
    if not api_key:
        raise ValueError("GROQ_API_KEY not found")
    return groq.Groq(api_key=api_key)

def generate_ai_response(messages, uploaded_materials=None):
    client = get_groq_client()
    
    system_content = "You are a helpful Study Mentor AI. Respond concisely and helpfully using Markdown formatting when appropriate."
    
    if uploaded_materials:
        system_content += "\n\nYou have access to these study materials:\n"
        for material in uploaded_materials:
            system_content += f"\n--- {material['name']} ---\n{material['content'][:3000]}\n"
    
    api_messages = [{"role": "system", "content": system_content}]
    api_messages.extend(messages)
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=api_messages,
            max_tokens=1000,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"AI API Error: {str(e)}")