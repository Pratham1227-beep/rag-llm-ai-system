from flask import Flask, jsonify, request
from flask_cors import CORS
from app.config import DevelopmentConfig

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 1. Initialize CORS with explicit wildcard support
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=False,
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # 2. Guarantee CORS headers on ALL outgoing responses (including errors)
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin", "*")
        response.headers["Access-Control-Allow-Origin"] = origin or "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        return response

    # 3. Handle OPTIONS preflight requests globally
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = app.make_default_options_response()
            origin = request.headers.get("Origin", "*")
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            return response

    # 4. Global error handler ensuring JSON + CORS response
    @app.errorhandler(Exception)
    def handle_exception(e):
        response = jsonify({"error": str(e), "type": type(e).__name__})
        response.status_code = 500
        origin = request.headers.get("Origin", "*")
        response.headers["Access-Control-Allow-Origin"] = origin or "*"
        return response

    # 5. Register Blueprints
    from app.routes.api import api_bp
    app.register_blueprint(api_bp)

    @app.route('/')
    def root():
        return {
            "status": "online",
            "message": "Enterprise RAG AI System Backend is running.",
            "health_check": "/api/health"
        }

    return app