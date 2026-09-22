from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app.services import ai_service, file_service, vector_service

# Define Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_configured": bool(current_app.config['GROQ_API_KEY']),
        "vector_db": vector_service.get_vector_db_stats()
    })

@api_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'messages' not in data:
            return jsonify({"error": "Missing 'messages'"}), 400

        result = ai_service.generate_ai_response(
            data['messages'],
            data.get('uploaded_materials', [])
        )

        content = result["content"] if isinstance(result, dict) else result
        sources = result.get("sources", []) if isinstance(result, dict) else []
        retrieved_count = result.get("retrieved_chunks_count", 0) if isinstance(result, dict) else 0

        return jsonify({
            "response": content,
            "sources": sources,
            "retrieved_chunks_count": retrieved_count,
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

        db_stats = vector_service.get_vector_db_stats()

        return jsonify({
            "files": processed_files,
            "count": len(processed_files),
            "vector_db": db_stats,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/vector-db/stats', methods=['GET'])
def vector_db_stats():
    """Returns vector database chunk statistics and ingested document details."""
    try:
        stats = vector_service.get_vector_db_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/vector-db/clear', methods=['POST'])
def clear_vector_db():
    """Resets the vector database."""
    try:
        result = vector_service.clear_vector_db()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500