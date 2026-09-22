from flask import Flask
from flask_cors import CORS
from app.config import DevelopmentConfig
from app.extensions import db, bcrypt, jwt


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Extensions
    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Register Blueprints
    from app.routes.api import api_bp
    from app.routes.auth import auth_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)

    # Create DB tables
    with app.app_context():
        from app.models.user import User  # noqa: ensure model is imported
        db.create_all()

    @app.route('/')
    def root():
        return {
            "status": "online",
            "message": "Enterprise RAG AI System Backend is running.",
            "health_check": "/api/health"
        }

    return app