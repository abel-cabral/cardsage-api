import redis
import json
import os

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..shared.util import purificarHTML
from ..shared.mongodb import adicionar_card, collection, todos_cards, deletar_card_por_id, atualizar_card
from ..shared.mongodb_search import search_query, search_tags
from ..shared.worker import processar_item
from ..shared.cache_utils import update_cache

main = Blueprint('main', __name__)

r = redis.Redis.from_url(os.getenv('REDIS_URL'))

_CAMPOS_PRIVADOS = {'operacaoMongo', 'conteudo', 'palavras_chaves', 'embedding'}


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

    if collection().find_one({"user_id": user_id, "cards.url": url}):
        return jsonify("Já existe uma URL associada a este usuário"), 409

    html_texto = purificarHTML(html)
    resultado = processar_item(user_id, url, html_texto)

    if not resultado:
        return jsonify("Erro ao processar e salvar dados."), 500

    update_cache(user_id)

    resposta = {k: v for k, v in resultado.items() if k not in _CAMPOS_PRIVADOS}
    return jsonify(resposta), 201


@main.route('/api/list-items', methods=['GET'])
@jwt_required()
def get_items():
    user_id = get_jwt_identity()
    cached_data = r.get(user_id)

    if cached_data:
        data = json.loads(cached_data.decode('utf-8'))
        return jsonify(data), 200

    items_json = todos_cards(user_id)
    r.set(user_id, items_json)
    return items_json, 200


@main.route('/api/search-items/<string:query>', methods=['GET'])
@jwt_required()
def search_items(query):
    items = search_query(query)
    return jsonify(items), 200


@main.route('/api/search-tags-items', methods=['GET'])
@jwt_required()
def search_tags_items():
    tags_param = request.args.get('tags', '')
    if not tags_param:
        return jsonify({"msg": "Parâmetro 'tags' é obrigatório (ex: ?tags=JavaScript,Python)"}), 400

    tags = [t.strip() for t in tags_param.split(',') if t.strip()]
    items = search_tags(tags)
    return jsonify(items), 200


@main.route('/api/update-item', methods=['PUT'])
@jwt_required()
def update_item():
    data = request.get_json()
    imageUrl = data.get('imageUrl', '')
    card_id = data.get('card_id', '')

    if not imageUrl:
        return jsonify("Necessário passar um campo 'imageUrl' no json"), 422
    if not card_id:
        return jsonify("Necessário passar um campo 'card_id' no json"), 422

    user_id = get_jwt_identity()

    if not collection().find_one({"user_id": user_id, "cards._id": card_id}):
        return jsonify("Item não encontrado no banco de dados ou usuário não autorizado"), 404

    resultado = atualizar_card(card_id, imageUrl, user_id)

    if resultado.modified_count == 0:
        return jsonify("Nenhum documento foi atualizado. Verifique os parâmetros fornecidos."), 400

    update_cache(user_id)
    return '', 204


@main.route('/api/delete-item/<string:card_id>', methods=['DELETE'])
@jwt_required()
def delete_item(card_id):
    user_id = get_jwt_identity()

    if not collection().find_one({"user_id": user_id, "cards._id": card_id}):
        return jsonify("Item não encontrado no banco de dados ou usuário não autorizado"), 404

    response = deletar_card_por_id(user_id, card_id)
    update_cache(user_id)
    return jsonify(response), 200
