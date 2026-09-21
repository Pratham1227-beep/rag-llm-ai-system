from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app.services import ai_service, file_service

# Define Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_configured": bool(current_app.config['GROQ_API_KEY'])
    })

@api_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'messages' not in data:
            return jsonify({"error": "Missing 'messages'"}), 400
            
        response = ai_service.generate_ai_response(
            data['messages'], 
            data.get('uploaded_materials', [])
        )
        
        return jsonify({
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400
        
        files = request.files.getlist('files')
        processed_files = []
        
        for file in files:
            if file.filename == '': continue
            try:
                result = file_service.process_uploaded_file(file)
                processed_files.append(result)
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
                
        return jsonify({
            "files": processed_files,
            "count": len(processed_files),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500