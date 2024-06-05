import os

from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from .jwt_config import configure_jwt
from .shared import collection
from .routes.auth import auth_bp
from .routes.routes import main

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure JWT
    configure_jwt(app)
    
    # initCache(app)
    
    app.register_blueprint(main)
    app.register_blueprint(auth_bp)
    
     # Carrega os dados do banco de dados e armazena na variável global
    response = collection('tags-raizes').find()
    os.environ['TAGLIST'] = ", ".join((list(response))[0]['TagsBase'])
    return app