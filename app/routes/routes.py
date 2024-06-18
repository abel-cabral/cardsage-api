import asyncio
import redis
import json
import os

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..shared.util import purificarHTML
from ..shared.chatgpt import iniciarConversa, classificarTagsGerais
from ..shared.mongodb import adicionar_ramo, collection, todos_ramos, deletar_ramo_por_id, atualizar_ramo
from bson.objectid import ObjectId
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
    html = data.get('html', '')
    
    if not url:
       return jsonify("Necessário passar um campo 'url' no json"), 422
   
    if not html:
        return jsonify("Necessário passar um campo 'html' no json"), 422
    
    # Verifica se a URL já existe no banco para o usuário logado
    user_id = get_jwt_identity()
    documento_existente = collection().find_one({"user_id": user_id, "ramos.url": url})
    if documento_existente:
        return jsonify("Já existe uma URL associado a este usuário"), 409
    
    # Extrai TEXTO HTML da URL
    html_texto = purificarHTML(html)
    
    # EXTRAINDO TAGS, RESUMO E DESCRIÇÃO
    chatHtml = asyncio.run(iniciarConversa(html_texto))
    
    chatData = json.loads(chatHtml)
    chatData['imageUrl'] = 'https://images.unsplash.com/photo-1557724630-96de91632c3b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2MTg2MTd8MHwxfHNlYXJjaHwxfHx1bmRlZmluZWR8ZW58MHwwfHx8MTcxNzg2MzEzMnww&ixlib=rb-4.0.3&q=80&w=1080'
    chatData['url'] = url
    
    tagData = [chatData['tag1'], chatData['tag2'], chatData['tag3']]
    tag = asyncio.run(classificarTagsGerais(chatData['descricao']))
    
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
    cache_key = get_jwt_identity()
    cached_data = r.get(cache_key)
    if cached_data:
        return json.loads(cached_data), 200
    else:
        items = todos_ramos()
        r.set(cache_key, items)
        return jsonify(json.loads(items)), 200

@main.route('/api/atualizar-item', methods=['PUT'])
@jwt_required()
def update_item():
    # Tratando a requisição e validando
    data = request.get_json()
    imageUrl = data.get('imageUrl', '')
    ramo_id = data.get('ramo_id', '')

    if not imageUrl:
        return jsonify("Necessário passar um campo 'imageUrl' no json"), 422

    if not ramo_id:
        return jsonify("Necessário passar um campo 'ramo_id' no json"), 422

    # Busca pela tag no banco que esteja relacionada ao usuario logado e com id do ramo valido
    user_id = get_jwt_identity()
    documento_existente = collection().find_one({"user_id": user_id, "ramos._id": ramo_id})

    if not documento_existente:
        return jsonify("Item não encontrado no banco de dados ou usuário não autorizado"), 404

    # Atualizando o campo imageUrl no ramo específico
    resultado = atualizar_ramo(ramo_id, imageUrl, user_id)

    # Verificar se a atualização foi bem-sucedida
    if resultado.modified_count == 0:
        return jsonify("Nenhum documento foi atualizado. Verifique os parâmetros fornecidos."), 400

    # Atualiza o cache após a atualização (implementação da função update_cache)
    update_cache()

    return '', 204

@main.route('/api/delete-item/<string:ramo_id>', methods=['DELETE'])
@jwt_required()
def delete_item(ramo_id):
    # Busca pelo id no banco que esteja relacionada ao usuario logado
    user_id = get_jwt_identity()
    documento_existente = collection().find_one({"user_id": user_id, "ramos._id": ramo_id})

    if not documento_existente:
        return jsonify("Item não encontrado no banco de dados ou usuário não autorizado"), 404
    
    response = deletar_ramo_por_id(ramo_id)
    
    # Invalida o cache para a rota de listagem de itens
    r.delete(get_jwt_identity())
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
    cache_key = get_jwt_identity()
    items = todos_ramos()
    r.set(cache_key, items)