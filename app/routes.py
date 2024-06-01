import asyncio
import json
import os

from flask import Blueprint, jsonify, request
from .shared.util import purificarHTML, partirHTML
from .shared.chatgpt import iniciarConversa, classificarTagsGerais
from .shared.mongodb import adicionar_ramo
from dotenv import load_dotenv

load_dotenv()

main = Blueprint('main', __name__)

# Dados de exemplo
items = [
    {'id': 1, 'name': 'Item 1', 'price': 10.0},
    {'id': 2, 'name': 'Item 2', 'price': 20.0},
]

@main.route('/api/items', methods=['GET'])
def get_items():
    return jsonify(items)

@main.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if item:
        return jsonify(item)
    else:
        return jsonify({'message': 'Item not found'}), 404

@main.route('/api/html', methods=['POST'])
def create_item():
    # Tratando o HTML
    data = request.get_json()
    htmlPurificado = purificarHTML(data.get('html', ''))
    
    # Extraindo Tags, Resumo e Descrição
    chatHtml = asyncio.run(iniciarConversa(htmlPurificado))
    chatData = json.loads(chatHtml.choices[0].message.content)
    
    tagData = [chatData['tag1'], chatData['tag2'], chatData['tag3']]
    tagExtracted = asyncio.run(classificarTagsGerais(os.getenv('TAGLIST').split(", "), tagData))
    tag = tagExtracted.choices[0].message.content
    
    # Salvando no Banco de Dados
    response = adicionar_ramo(tag, chatData)
    
    return jsonify(response), 201

@main.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = next((item for item in items if item['id'] == item_id), None)
    if item:
        data = request.get_json()
        item.update(data)
        return jsonify(item)
    else:
        return jsonify({'message': 'Item not found'}), 404

@main.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    global items
    items = [item for item in items if item['id'] != item_id]
    return jsonify({'message': 'Item deleted'})