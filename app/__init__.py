import os
import json

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from config import Config
from .jwt_config import configure_jwt
from .shared import collection
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
    
    # Carrega os dados do banco de dados e armazena na variável global
    response = collection('tags-raizes').find()
    tags_base = [tag for doc in response for tag in doc['TagsBase']]  # Desempacota as listas internas
    os.environ['TAGLIST'] = ", ".join(str(tag) for tag in tags_base)  # Converte cada tag para uma string
    
    # Imprimir os valores de TagsBase
    print(os.environ['TAGLIST'].split(','))
    
    return app