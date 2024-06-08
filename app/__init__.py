from flask import Flask
from config import Config
from .jwt_config import configure_jwt
from .routes.auth import auth_bp
from .routes.routes import main
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure JWT
    configure_jwt(app)
    
    # Enable CORS for the app
    CORS(app)
    
    app.register_blueprint(main)
    app.register_blueprint(auth_bp)
    return app