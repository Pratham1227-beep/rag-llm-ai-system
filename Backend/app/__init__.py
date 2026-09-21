from flask import Flask
from flask_cors import CORS
from app.config import DevelopmentConfig

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Extensions
    CORS(app)
    
    # Register Blueprints
    from app.routes.api import api_bp
    app.register_blueprint(api_bp)
    
    return app