import asyncio
import redis
import json
import os

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..shared.util import purificarHTML
from ..shared.chatgpt import iniciarConversa, classificarTagsGerais
from ..shared.mongodb import adicionar_ramo, collection, todos_ramos, deletar_ramo_por_id
from ..shared.selenium_html_extractor import html_extrator
from dotenv import load_dotenv

load_dotenv()

main = Blueprint('main', __name__)

# Criar uma instância do cliente Redis
r = redis.Redis.from_url(os.getenv('REDIS_URL'))

@main.route('/api/save-item', methods=['POST'])
@jwt_required()
def create_item():
    # TRATANDO O REQUISIÇÃO E VALIDANDO
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
       return jsonify("Necessário passar um campo 'url' no json"), 422
    
    # Verifica se a URL já existe no banco para o usuário logado
    user_id = get_jwt_identity()
    documento_existente = collection().find_one({"url": url, "user_id": user_id})
    if documento_existente:
        return jsonify("Já existe uma URL associado a este usuário"), 409
    
    # Extrai TEXTO HTML da URL
    html_texto = html_extrator(url)
    
    # EXTRAINDO TAGS, RESUMO E DESCRIÇÃO
    chatHtml = asyncio.run(iniciarConversa(html_texto))
    chatData = json.loads(chatHtml.choices[0].message.content)
    chatData['url'] = url
    
    tagData = [chatData['tag1'], chatData['tag2'], chatData['tag3']]
    tagExtracted = asyncio.run(classificarTagsGerais(os.getenv('TAGLIST').split(", "), chatData['descricao']))
    tag = tagExtracted.choices[0].message.content
    
    # SALVANDO NO BANCO DE DADOS
    mongo_response = adicionar_ramo(tag, chatData)
    
    if 'message' in mongo_response:
        return mongo_response['message'], 415
    
    # Atualiza o cache após a inclusão de um novo ramo
    update_cache()
    
    # TRATANDO O RETORNO
    response = mongo_response['ramos'][-1]
    response['tag_raiz'] = mongo_response['tag_raiz']
    
    return jsonify(response), 201

@main.route('/api/list-items', methods=['GET'])
@jwt_required()
def get_items():
    # Use uma chave única para representar os dados que deseja armazenar em cache
    cache_key = 'list_items'
    cached_data = r.get(cache_key)
    if cached_data:
        return json.loads(cached_data), 200
    else:
        items = todos_ramos()
        r.set(cache_key, items)
        return jsonify(json.loads(items)), 200

@main.route('/api/delete-item/<string:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    response = deletar_ramo_por_id(item_id)
    # Invalida o cache para a rota de listagem de itens
    r.delete('list_items')
    return jsonify(response), 204

@main.route('/api/redis-keys', methods=['GET'])
def redis_keys():
    try:
        # Obtém todas as chaves armazenadas no Redis
        keys = r.keys('*')
        # Cria um dicionário para armazenar as chaves e seus valores
        cache_contents = {}
        for key in keys:
            cache_contents[key.decode('utf-8')] = r.get(key).decode('utf-8')
        
        return jsonify(cache_contents), 200
    except Exception as e:
        return jsonify({"message": "Error accessing Redis", "error": str(e)}), 500

def update_cache():
    # Atualiza o cache para a lista de itens
    cache_key = 'list_items'
    items = todos_ramos()
    r.set(cache_key, items)