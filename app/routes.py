import asyncio
import json
import os

from flask import Blueprint, jsonify, request
from .shared.util import purificarHTML, partirHTML
from .shared.chatgpt import iniciarConversa, classificarTagsGerais
from .shared.mongodb import adicionar_ramo, collection, todos_ramos, deletar_ramo_por_id
from .shared.html_extractor import extrair_texto_visivel
from dotenv import load_dotenv

load_dotenv()

main = Blueprint('main', __name__)

@main.route('/api/save-item', methods=['POST'])
def create_item():
    # TRATANDO O REQUISIÇÃO E VALIDANDO
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
       return jsonify("Necessário passar um campo 'url' no json"), 422
    
    # VERIFICA SE URL JÁ EXISTE NO BANCO
    documento_existente = collection().find_one({"url": url})
    if documento_existente:
        return jsonify("Já existente no banco de dados"), 409
    
    # Extrai TEXTO HTML da URL
    htmlPurificado = extrair_texto_visivel(url)
    
    # EXTRAINDO TAGS, RESUMO E DESCRIÇÃO
    chatHtml = asyncio.run(iniciarConversa(htmlPurificado))
    chatData = json.loads(chatHtml.choices[0].message.content)
    chatData['url'] = url
    
    tagData = [chatData['tag1'], chatData['tag2'], chatData['tag3']]
    tagExtracted = asyncio.run(classificarTagsGerais(os.getenv('TAGLIST').split(", "), chatData['descricao']))
    tag = tagExtracted.choices[0].message.content
    
    # SALVANDO NO BANCO DE DADOS
    mongo_response = adicionar_ramo(tag, chatData)
    
    if 'message' in mongo_response:
        return mongo_response['message'], 415
    
    # Tratando retorno
    response = mongo_response['ramos'][len(mongo_response['ramos']) - 1]
    response['tag_raiz'] = mongo_response['tag_raiz']
    
    return jsonify(response), 201

@main.route('/api/list-items', methods=['GET'])
def get_items():
    items = todos_ramos()
    return jsonify(json.loads(items)), 201

@main.route('/api/delete-item/<string:item_id>', methods=['DELETE'])
def delete_item(item_id):
    response = deletar_ramo_por_id(item_id)
    return jsonify(response)