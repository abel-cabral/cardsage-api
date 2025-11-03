import asyncio
import redis
import json
import os

from flask import Blueprint, jsonify, request
from rq import Queue
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..shared.util import purificarHTML
from ..shared.chatgpt import iniciarConversa, classificarTagsGerais
from ..shared.mongodb import adicionar_card, collection, todos_cards, deletar_card_por_id, atualizar_card
from bson.objectid import ObjectId
from dotenv import load_dotenv
from ..shared.mongodb_search import search_query, search_tags
from ..shared.worker import processar_item
from ..shared.cache_utils import update_cache

load_dotenv()

main = Blueprint('main', __name__)

# Criar uma instância do cliente Redis
r = redis.Redis.from_url(os.getenv('REDIS_URL'))

# Cria uma fila no Redis
q = Queue('processar_fila', connection=r)

@main.route('/api/save-item', methods=['POST'])
@jwt_required()
def create_item():
    data = request.get_json()
    url = data.get('url', '')
    html = data.get('html', '')

    if not url:
        return jsonify("Necessário passar um campo 'url' no json"), 422
    if not html:
        return jsonify("Necessário passar um campo 'html' no json"), 422

    user_id = get_jwt_identity()
    documento_existente = collection().find_one({"user_id": user_id, "cards.url": url})
    if documento_existente:
        return jsonify("Já existe uma URL associada a este usuário"), 409

    html_texto = purificarHTML(html)

    # 🔹 Enfileira o processamento
    job = q.enqueue(processar_item, user_id, url, html_texto, job_timeout=1000)

    # Polling para esperar o job terminar
    while not job.is_finished and not job.is_failed:
        import time
        time.sleep(1)
    
    if job.is_failed:
        return jsonify({"message": "Erro ao processar o item"}), 500
    
    # Retorno do valor processado
    return jsonify(job.result), 201

@main.route('/api/list-items', methods=['GET'])
@jwt_required()
def get_items():
    # Use uma chave única para representar os dados que deseja armazenar em cache
    #user_id = get_jwt_identity()
    #cached_data = r.get(user_id)

    user_id = get_jwt_identity()
    items = todos_cards(user_id)
    return items, 200

    # if cached_data:
    #     # Decodifica os dados de bytes para string antes de carregá-los como JSON
    #     data = json.loads(cached_data.decode('utf-8'))
    #     return data, 200
    # else:
    #     # Use uma chave única para representar os dados que deseja armazenar em cache
    #     user_id = get_jwt_identity()
    #     items = todos_cards(user_id)
    #     return items, 200

@main.route('/api/search-items/<string:query>', methods=['GET'])
@jwt_required()
def search_items(query):
    items = search_query(query)
    return items, 200

@main.route('/api/search-tags-items', methods=['GET'])
@jwt_required()
def search_tags_items():
     # Exemplo de pesquisa por tags
    tags_pesquisa = ['JavaScript']
    items = search_tags(tags_pesquisa)
    return items, 200

@main.route('/api/update-item', methods=['PUT'])
@jwt_required()
def update_item():
    # Tratando a requisição e validando
    data = request.get_json()
    imageUrl = data.get('imageUrl', '')
    card_id = data.get('card_id', '')

    if not imageUrl:
        return jsonify("Necessário passar um campo 'imageUrl' no json"), 422

    if not card_id:
        return jsonify("Necessário passar um campo 'card_id' no json"), 422
    
    # Busca pela tag no banco que esteja relacionada ao usuario logado e com id do card valido
    user_id = get_jwt_identity()
    documento_existente = collection().find_one({"user_id": user_id, "cards._id": card_id})

    if not documento_existente:
        return jsonify("Item não encontrado no banco de dados ou usuário não autorizado"), 404

    # Atualizando o campo imageUrl no card específico
    resultado = atualizar_card(card_id, imageUrl, user_id)

    # Verificar se a atualização foi bem-sucedida
    if resultado.modified_count == 0:
        return jsonify("Nenhum documento foi atualizado. Verifique os parâmetros fornecidos."), 400

    # Atualiza o cache após a atualização (implementação da função update_cache)
    #update_cache(user_id)

    return '', 204

@main.route('/api/delete-item/<string:card_id>', methods=['DELETE'])
@jwt_required()
def delete_item(card_id):
    # Busca pelo id no banco que esteja relacionada ao usuario logado
    user_id = get_jwt_identity()
    documento_existente = collection().find_one({"user_id": user_id, "cards._id": card_id})

    if not documento_existente:
        return jsonify("Item não encontrado no banco de dados ou usuário não autorizado"), 404
    
    response = deletar_card_por_id(user_id, card_id)
    
    # Atualiza o cache para a rota de listagem de itens
    #update_cache(user_id)
    return response, 200