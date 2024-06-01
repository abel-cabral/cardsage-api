import os

from flask import Flask
from .routes import main
from .shared import collection

tagsRaizes = []
def create_app():
    app = Flask(__name__)
    app.register_blueprint(main)
    
     # Carrega os dados do banco de dados e armazena na variável global
    response = collection('tags-raizes').find()
    os.environ['TAGLIST'] = ", ".join((list(response))[0]['TagsBase'])
    return app